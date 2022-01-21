//ทำการ import express เข้ามาใช้งาน โดยสร้างตัวแปร express ขึ้นมาเพื่อรับค่า
// import libraries 
var json = require('./dataJSON.json');
var json1 = require('./person.json');
const express = require('express')
const path = require('path');
const moment = require('moment')
var http = require('http');
var cors = require('cors')
bodyParser = require('body-parser');
var cookieParser = require('cookie-parser')
const app = express()
const PORT = process.env.PORT || 8080
app.use(bodyParser.json());
// ################################ JWT token
const jwtSecret = 'BHH_SEPSIS';
const jwt = require('express-jwt');
const jsonwebtoken = require('jsonwebtoken');
const csrf = require('csurf')
var CryptoJS = require("crypto-js");
app.use(cors({ origin: true, credentials: true })); //don't forget


// ################################ Database BHH can read only
// ################################ Connect database from BDMS (wifi: BDMS_APP)
const { Client } = require('pg');
const connectionString = 'postgres://bhhsepsis:sepsis@bhh@10.141.13.3:5432/imed_bhh';
const sepsisdb = new Client({connectionString: connectionString});
sepsisdb.connect();

// ################################ Database BHH can insert delete update
const connectionString2 = 'postgres://bhhsepsis:sepsis@bhh@10.141.13.2:5432/imed_bhh';
const sepsisdb2 = new Client({connectionString: connectionString2});
sepsisdb2.connect();


// ################################ Database Sepsis
// const conString = "postgres://YourUserName:YourPassword@YourHostname:5432/YourDatabaseName";
const connectionString3 = "postgres://sepsis_tqc:tqc_sepsis@10.141.10.17:5432/sepsis_db";
const sepsisdb3 = new Client({connectionString: connectionString3});
sepsisdb3.connect();

// ################################ Authentication
app.get('/api/login',async (req, res) => {
    //console.log(req.query.user)
    //console.log(req.query.pass)

    // work for cookies token
    const token = jsonwebtoken.sign({ user: req.query.user }, jwtSecret);
    //console.log('Cookies: ', req.cookies) 
    const auth = {token:'', status:'',user:''}
    // res.json({ auth });

    if(req.query.user && req.query.pass){

        var bytes  = CryptoJS.AES.decrypt(req.query.pass, '_tqc');
        var originalText = bytes.toString(CryptoJS.enc.Utf8);
        
        //console.log(originalText); // 'my message'
        
        const sql = `SELECT public.bhh_sepsis_json_login('${req.query.user}','${originalText}')`;
        const result = await sepsisdb.query(sql)
        //console.log(result)
        //console.log(result)
        //console.log(JSON.parse(result.rows[0]['bhh_sepsis_json_login']))
        if(result.rows[0]['bhh_sepsis_json_login'] !=  '{}' ){

            //console.log('true')
            // const token = jsonwebtoken.sign({ user: req.query.user }, jwtSecret);
            //console.log('Cookies: ', token) 
            res.cookie('_tqc', token, { 
                maxAge: 7200000, // 2 hours
                secure: false, // set to true if your using https
                httpOnly: true });
            auth.token=null
            auth.status=200
            auth.user=result.rows[0]
            // res.setHeader('_tqc', token, { maxAge: 900000,httpOnly: true });
            res.json({ auth });

        }else{
            //console.log('false')
            auth.token=null
            auth.status=401
            auth.user=null
            res.json({ auth });
        }

    }else{
        //console.log('false')
        auth.token=null
        auth.status=401
        auth.user=null
        res.json({ auth });
    }

});


app.get('/api/test', (req, res) => {
    //console.log("test")
    //console.log('Cookies: ', req.cookies) 
    // res.json(200)
    
});

// compliance select report
app.post('/api/compliance_select', (req, res) =>{
    try{

        //console.log(req.body.start)
        //console.log(req.body.end)
        //console.log(req.body.diag)

        //console.log(req.body.diag.length)

        var where1 = ``
        var where2= ``

        if(req.body.diag.length===0){
        
            where1 =``

        }else if(req.body.diag.length===1){
            where1 =`ds.diagnosis_status in ('Sepsis')`

        }else if(req.body.diag.length===2){
            where1 =`ds.diagnosis_status in ('Sepsis','Non-sepsis')`
        }

        // if(typeof req.body.parameter == "string"){
            const sql = `
            SELECT ds.row_id,
            to_char(ds.unfollow_time, 'YYYY-MM-DD HH24:MI')as unfollow_time,
            to_char(cs.datetime_follow, 'YYYY-MM-DD HH24:MI')as datetime_follow,
            to_char(ds.diagnosis_time, 'YYYY-MM-DD HH24:MI')as diagnosis_time,
            diagnosis_status,
            to_char(cs.datetime, 'YYYY-MM-DD HH24:MI')as compliance_time,
            ds.hn_patient as hn, ds.an_patient as an,ds.room_id ,
            css.qsofa,
            css.history_admit,
            css.history_atb,
            css.history_infection,
            css.history_map,
            css.history,
            css.lactate,
            css.atb,
            css.specimen,
            css.image,
            css.lab,
            css.atbhr,
            css.bolus,
            css.vasopressors,
            css.follow,
            css.goalachieve,
            css.treatment,
            css.atb_guide,
            css.abnormal,
            css.followup,
            css.disease,
            css.nutrition,
            css.discharge,
            css.total_compliance,
            css.staff_id,
            css.note
            FROM public.diagnosis_sepsis ds
            left join 
                (
                select an_patient, min(datetime_follow) as datetime_follow, max(datetime) as datetime, max(row_id) as row_id  
                from public.compliance_sepsis
                group by an_patient 
                ) cs
            on ds.an_patient = cs.an_patient
            join public.compliance_sepsis css on cs.row_id = css.row_id
            where cs.datetime_follow between '${req.body.start}' and '${req.body.end}'
            `
            // where ${where1} and cs.datetime_follow between '${req.body.start}' and '${req.body.end}'
            // const sql = "SELECT * FROM pg_catalog.pg_tables";
            sepsisdb3.query(sql, function (err, result) {
                if (err) {
                    console.log(err);
                    res.status(400).send(err);
                }
                // convert sting to object 
                // const obj = JSON.parse(result.rows[0]);
                // response status and data
                //console.log(result.rows)
                res.status(200).send(result.rows);
            })
        // }
    }catch(e){
        //console.log(e)
        res.status(400)
    }
    

});




// ################################ Protection zone
app.use(cookieParser()); //don't forget
app.use('/api',jwt({ secret: jwtSecret,getToken: req => req.cookies._tqc, algorithms: ['HS256'] }).unless({path: ['/api/test']})); //don't forget

// ################################ Fetch data
// function mornitor
function mornitor(ward){
    //console.log("interval ward")
    const parameter = ['07W08'];
    const sql = "SELECT public.bhh_sepsis_json_monitor()";
    const vitalsign = "SELECT public.bhh_sepsis_json_vitalsign_by_an($1)"
    // parameter [HN,AN,Status]
    
    
    sepsisdb.query(sql,function (err, result) {
        if (err) {
            console.log(err);
            res.status(400).send(err);
        }

        // //console.log(result.rows[0]['bhh_sepsis_json_monitor'])
        if(result.rows[0]['bhh_sepsis_json_monitor'] !== '{}'){
            const obj = JSON.parse(result.rows[0]['bhh_sepsis_json_monitor']);    
            var result = [...new Map(obj.map(x => [x.HN, x])).values()]
            let red = 3
            let orange = 2 
            let green = 1
            let white = 0
            let color =0
            var id =[]
            var value = []

            for (var i = 0; i < result.length; i++) {
                value[i] = `('${result[i].HN}','${result[i].AN}','${result[i].Bed}',CURRENT_TIMESTAMP,'active','','')` 
                // (hn_patient, an_patient, room_id, datetime, status, staff_id, name_patient)
            }

            const insert = `with data(hn_patient, an_patient, room_id, datetime, status, staff_id, name_patient)  as (
                values  ${value}) 
                INSERT INTO public.follow_sepsis(hn_patient, an_patient, room_id, datetime, status, staff_id, name_patient)
                select *
                from data
                where an_patient not in (
                    select an_patient 
                    from public.follow_sepsis 
                    where datetime::timestamp > to_char(current_timestamp, 'YYYY-MM-DD HH24:MM:SS')::timestamp - "interval" '1 hours') 
                and datetime > to_char(current_timestamp, 'YYYY-MM-DD HH24:MM:SS')::timestamp - "interval" '1 hours';`

            sepsisdb3.query(insert, function (err, result) {
                if (err) {
                    console.log(err);
                    res.status(400).send(err);
                }
            })
        }

    })

    
}

// interval mornitor
var interval = setInterval(mornitor,600000)
// var interval = setInterval(mornitor,5000)

// ################################ Data
// get data onward 
app.get('/api/ward', (req, res) => {

    const parameter = ['07W08'];
    const sql = "SELECT public.bhh_sepsis_json_bed_by_ward($1)";
    sepsisdb.query(sql, parameter, function (err, result) {
        if (err) {
            console.log(err);
            res.status(400).send(err);
        }
        // convert sting to object 
        const obj = JSON.parse(result.rows[0]['bhh_sepsis_json_bed_by_ward']);
        // response status and data
        res.status(200).send(obj);
    })

})

// mornitor
app.get('/api/mornitor', (req, res) => {
    const ward = ['07W08'];
    // mornitor(ward)

    //console.log("interval ward")
    const parameter = [ward];
    const sql = "SELECT public.bhh_sepsis_json_monitor()";
    const vitalsign = "SELECT public.bhh_sepsis_json_vitalsign_by_an($1)"
    // parameter [HN,AN,Status]
    
    
    sepsisdb.query(sql,function (err, result) {
        if (err) {
            console.log(err);
            res.status(400).send(err);
        }

        //console.log(result.rows[0]['bhh_sepsis_json_monitor'])
        if(result.rows[0]['bhh_sepsis_json_monitor'] !== '{}'){
            const obj = JSON.parse(result.rows[0]['bhh_sepsis_json_monitor']);    
            var result = [...new Map(obj.map(x => [x.HN, x])).values()]
            let red = 3
            let orange = 2 
            let green = 1
            let white = 0
            let color =0
            var id =[]
            var value = []

            for (var i = 0; i < result.length; i++) {
                value[i] = `('${result[i].HN}','${result[i].AN}','${result[i].Bed}',CURRENT_TIMESTAMP,'active','','')` 
                // (hn_patient, an_patient, room_id, datetime, status, staff_id, name_patient)
            }

            const insert = `with data(hn_patient, an_patient, room_id, datetime, status, staff_id, name_patient)  as (
                values  ${value}) 
                INSERT INTO public.follow_sepsis(hn_patient, an_patient, room_id, datetime, status, staff_id, name_patient)
                select *
                from data
                where an_patient not in (
                    select an_patient 
                    from public.follow_sepsis 
                    where datetime::timestamp > to_char(current_timestamp, 'YYYY-MM-DD HH24:MM:SS')::timestamp - "interval" '1 hours') 
                and datetime > to_char(current_timestamp, 'YYYY-MM-DD HH24:MM:SS')::timestamp - "interval" '1 hours';`

            //console.log(insert)

            sepsisdb3.query(insert, function (err, result) {
                if (err) {
                    console.log(err);
                    res.status(400).send(err);
                }
            })


            for (var i = 0; i < result.length; i++) {

            var newscore = 0

                if(result[i].RR<=8){
                    newscore =newscore+red

                }else if(result[i].RR>=9 && result[i].RR<=11){
                    newscore = newscore+green

                }else if(result[i].RR>=12&&result[i].RR<=20){
                    newscore = newscore+white

                }else if(result[i].RR>=21&&result[i].RR<=24){
                    newscore = newscore+orange

                }else if(result[i].RR>=25){
                    newscore = newscore+red
                }

                if(result[i].O2Sat<=91){
                    newscore =newscore+red
    
                }else if(result[i].O2Sat>=92 && result[i].O2Sat<=93){
                    newscore = newscore+orange

                }else if(result[i].O2Sat>=94&&result[i].O2Sat<=95){
                    newscore = newscore+green

                }else if(result[i].O2Sat>=96){
                    newscore = newscore+white

                }


                if(result[i].cur_temp<=35){
                    newscore = newscore+red 
                }else if(result[i].cur_temp>=35.1 && result[i].cur_temp<=36.0){
                    newscore = newscore+green
                }else if(result[i].cur_temp>=36.1 && result[i].cur_temp<=38.0){
                    newscore = newscore+white
                }else if(result[i].cur_temp>=38.1 && result[i].cur_temp<=39.0){
                    newscore = newscore+green
                }else if(result[i].cur_temp>=39.1){
                    newscore = newscore+orange
                }

                if(result[i].SYS<=90){
                    newscore =newscore+red 
                }else if(result[i].SYS>=91 && result[i].SYS<=100){
                    newscore = newscore+orange
                }else if(result[i].SYS>=101 && result[i].SYS<=110){
                    newscore = newscore+green
                }else if(result[i].SYS>=111 && result[i].SYS<=219){
                    newscore = newscore+white
                }else if(result[i].SYS>=220){
                    newscore = newscore+red
                }

                if(result[i].PR<=40){
                newscore = newscore+red 
                }else if(result[i].PR>=41 && result[i].PR<=50){
                newscore = newscore+green
                }else if(result[i].PR>=51 && result[i].PR<=90){
                newscore = newscore+white
                }else if(result[i].PR>=91 && result[i].PR<=110){
                newscore = newscore+green
                }else if(result[i].PR>=111 && result[i].PR<=130){
                newscore = newscore+orange
                }else if(result[i].PR>=131){
                newscore = newscore+red 
                }



                if(result[i].Consciousness=="A" || result[i].Consciousness=="a"){
                newscore = newscore+white
                color = white
                }
                else if(result[i].Consciousness==null){
                    newscore = newscore
                }
                else{
                    newscore = newscore+red
                    color = red
                }
            
            result[i].ss_news=newscore
            }
            //console.log(id)

            res.status(200).send(result);

        }else{
            res.status(200).send(result.rows[0]['bhh_sepsis_json_monitor']);
        }
    })
})

// get follow ward 
app.get('/api/follow_incriteria', (req, res) => {

    // const parameter = ['07W08'];

    
    const sql = `
    SELECT row_id,datetime,hn_patient as hn, an_patient as an, status as follow_status ,room_id 
    FROM public.follow_sepsis 
    where datetime::timestamp > to_char(current_timestamp, 'YYYY-MM-DD HH24:MM:SS')::timestamp - "interval" '1 hours' 
    and status = 'active' and an_patient not in (select an_patient from public.diagnosis_sepsis  where diagnosis_time::timestamp > to_char(current_timestamp, 'YYYY-MM-DD HH24:MM:SS')::timestamp - "interval" '8 hours')
    ;`;

    sepsisdb3.query(sql,function (err, result) {
        if (err) {
            console.log(err);
            res.status(400).send(err);
        }
        // convert sting to object 
        // const obj = JSON.parse(result.rows[0]);
        // response status and data
        res.status(200).send(result.rows);
    })

})

// get sepsis patient 
app.get('/api/follow_sepsis', (req, res) => {

    const sql = `    SELECT 
    ds.row_id,
    ds.unfollow_time,
    ds.diagnosis_time,
    ds.datetime_follow ,
    to_char(current_timestamp::timestamp - cs.datetime::timestamp, 'HH24 hr. MI m.') as time, 
    cs.datetime as compliance_time,
    ds.hn_patient as hn, 
    ds.an_patient as an,
    ds.room_id ,
    css.qsofa ,
    css.history, 
    css.lab, 
    css.treatment , 
    css.discharge
    FROM public.diagnosis_sepsis ds
    left join 
        (
        select an_patient, max(datetime) as datetime,max(row_id) as row_id  
        from public.compliance_sepsis
        group by an_patient 
        ) cs
    on ds.an_patient = cs.an_patient
    join public.compliance_sepsis css on cs.row_id = css.row_id
    where ds.diagnosis_status in ('Sepsis') and ds.unfollow_time is null;`
    sepsisdb3.query(sql,function (err, result) {
        if (err) {
            console.log(err);
            res.status(400).send(err);
        }
        // convert sting to object 
        // const obj = JSON.parse(result.rows[0]);
        // response status and data
        res.status(200).send(result.rows);
    })

})

app.get('/api/auth', (req, res) => {

    //console.log('Cookies: ', req.cookies) 
    res.json({status:200})

});

app.get('/api/destroy', (req, res) => {
    //console.log("destroy")
    //console.log('Cookies: ', req.cookies) 
    res.clearCookie("_tqc")
    res.json({status:200})
    // res.json(200)

});



// don't forget
const csrfProtection = csrf({
    cookie: true
});

app.use(csrfProtection);
app.use(function (req, res, next) {
    var token = req.csrfToken();
    res.cookie('XSRF-TOKEN', token);
    res.locals.csrfToken = token;
    next();
  });

app.get('/csrf-token', (req, res) => {
    res.json({ csrfToken: req.csrfToken() });
});

// get demographic ward 8
app.post('/api/info_patient',async (req, res) => {
    // //console.log(req.body.an)
    
    const parameter = [req.body.an];

    const demographic = `SELECT public.bhh_sepsis_json_demographics_by_an('${req.body.an}')`;
    const operation = `SELECT public.bhh_sepsis_json_operation_by_an('${req.body.an}')`;
    const vitalsign = `SELECT public.bhh_sepsis_json_vitalsign_by_an('${req.body.an}')`;

    try{
    
    const operation_json =  await sepsisdb.query(operation)
    const vitalsign_json =  await sepsisdb.query(vitalsign)
    const demographic_json = await sepsisdb.query(demographic)

    // //console.log("Demographic_json")
    // //console.log(demographic_json.rows[0]['bhh_sepsis_json_demographics_by_an'])
    // //console.log(operation_json.rows[0]['bhh_sepsis_json_operation_by_an'])
    // //console.log(vitalsign_json.rows[0]['bhh_sepsis_json_vitalsign_by_an'])
        
    res.json({
        demographic:demographic_json.rows[0]['bhh_sepsis_json_demographics_by_an'],
        operation:operation_json.rows[0]['bhh_sepsis_json_operation_by_an'],
        vitalsign:vitalsign_json.rows[0]['bhh_sepsis_json_vitalsign_by_an']
    })


    
    }catch(error){
        //console.log(error)
       
    }

    res.json({
        demographic:null,
        operation:null,
        vitalsign:null
    })

})

// get lab order
app.post('/api/lab_patient', (req, res) => {
    
    ////console.log("lab_patient")
    // //console.log("530:",req.body.an)
    if(req.body.an != "undefined"){
        const lab =`SELECT public.bhh_sepsis_json_lablist_by_an('${req.body.an}')`;

        sepsisdb.query(lab, function (err, result) {
            if (err) {
                // console.log(err);
                res.status(400).send(err);
            }
            res.json({
                lab_order:result.rows[0]['bhh_sepsis_json_lablist_by_an'],
            })
        })
    }else{
        res.status(500).json({
            lab_order:null
        })
    }


})

// get result lab
app.post('/api/followlab',async (req,res)=>{

    const lab =`SELECT public.bhh_sepsis_json_labresult_by_an('${req.body.an}')`;

    try{
    
        const result =  await sepsisdb.query(lab)
      

            
        var obj = JSON.parse(result.rows[0]['bhh_sepsis_json_labresult_by_an'])
        try{
        for (var i = 0; i < obj.length; i++) {

            obj[i].lab_result = obj[i].lab_result.replace(/\n|\r\n|\r/g, '<br/>')

        }
        }catch(e){
            //console.log(e)
        }

        res.json({
            lab_result : obj
        })
    
    
        
        }catch(error){
            //console.log(error)
           
        }



})

// get vitalsign patient 
app.post('/api/vitalsign', (req, res) => {
    
    const parameter = [req.body.an];

    const vitalsign = "SELECT public.bhh_sepsis_json_vitalsign_by_an($1)"



    sepsisdb.query(vitalsign, parameter, function (err, vitalsign_json) {
        if (err) {
            console.log(err);
            res.status(400).send(err);
        }else{
            res.json({
                vitalsign:vitalsign_json.rows[0]['bhh_sepsis_json_vitalsign_by_an']
            })
        }
    
    })
    
})

// post delete follow ward 
app.post('/api/send_compliance/0', (req, res) => {
    // //console.log(req.body.follow_id)
    // //console.log(req.body)
    var note = ''
    if(req.body.note == undefined){
        note=" "
    }else{
        note = req.body.note
    }
    const sql = `
    UPDATE public.follow_sepsis SET status='inactive' where row_id = '${req.body.follow_id}';
    INSERT INTO public.compliance_sepsis
    (
    follow_id,datetime_follow,
    hn_patient, an_patient, room_id, datetime, 
    staff_id, 
    note,
    qSOFA,
    history,history_admit,history_ATB,history_map,history_Infection,
    lab, lactate, ATB, specimen, image, 
    treatment,ATBhr, bolus, vasopressors, follow, goalachieve, 
    discharge,ATB_guide,Abnormal, followup,disease,nutrition, 
    total_compliance
    )
    VALUES('${req.body.follow_id}', '${req.body.datetime_follow}', 
    '${req.body.hn_patient}','${req.body.an_patient}','${req.body.room_id}', CURRENT_TIMESTAMP, 
    ${req.body.staff_id}, 
    '${note}',
    ${req.body.qSOFA},
    ${req.body.history},${req.body.history_admit},${req.body.history_ATB},${req.body.history_map},${req.body.history_Infection},
    ${req.body.lab},${req.body.lactate},${req.body.ATB},${req.body.specimen},${req.body.image},
    ${req.body.treatment},${req.body.ATBhr},${req.body.bolus},${req.body.vasopressors},${req.body.follow},${req.body.goalachieve},
    ${req.body.discharge},${req.body.ATB_guide},${req.body.Abnormal},${req.body.followup},${req.body.disease},${req.body.nutrition},
    ${req.body.total_compliance}
    );`;
    sepsisdb3.query(sql, function (err, result) {
        if (err) {
            console.log(err);
            res.status(400).send(err);
        }
        //console.log(result)
        res.status(200).send("finish")
    })

})

// post unfollow sepsis
app.post('/api/unfollow_sepsis', (req, res) => {
    //console.log(req.body.follow_id)
    const sql = `
    UPDATE public.diagnosis_sepsis SET unfollow_time=current_timestamp where row_id ='${req.body.follow_id}';`;
    sepsisdb3.query(sql, function (err, result) {
        if (err) {
            console.log(err);
            res.status(400).send(err);
        }
        //console.log(result)
        res.status(200).send("finish")
    })

})

// post diagnosis follow ward 
// get del follow ward 8
app.post('/api/diagnosis_sepsis', async (req, res) => {
    //console.log(req.body.follow_id)
    //console.log(req.body)
    const sql = `
    UPDATE public.follow_sepsis SET status='inactive' where row_id = '${req.body.follow_id}';
    INSERT INTO public.diagnosis_sepsis
    (
        follow_id,datetime_follow,
        hn_patient, an_patient, room_id, diagnosis_time,
        staff_id,
        diagnosis_status,unfollow_time,note
    )
    VALUES('${req.body.follow_id}', '${req.body.datetime_follow}', 
    '${req.body.hn_patient}','${req.body.an_patient}','${req.body.room_id}',CURRENT_TIMESTAMP,
    '${req.body.staff_id}',
    '${req.body.diagnosis_status}',null,'${req.body.note}'
    );
    INSERT INTO public.compliance_sepsis
    (
    follow_id,datetime_follow,
    hn_patient, an_patient, room_id, datetime, 
    staff_id, 
    note,
    qSOFA,
    history,history_admit,history_ATB,history_map,history_Infection,
    lab, lactate, ATB, specimen, image, 
    treatment,ATBhr, bolus, vasopressors, follow, goalachieve, 
    discharge,ATB_guide,Abnormal, followup,disease,nutrition, 
    total_compliance
    )
    VALUES('${req.body.follow_id}', '${req.body.datetime_follow}', 
    '${req.body.hn_patient}','${req.body.an_patient}','${req.body.room_id}', CURRENT_TIMESTAMP, 
    '${req.body.staff_id}',
    ' ',
     0,
     0,0,0,0,0,
     0,0,0,0,0,
     0,0,0,0,0,0,
     0,0,0,0,0,0,
     0);
    `;

    //console.log(sql)
    const result = await sepsisdb3.query(sql, function (err, result) {
        if (err) {
            console.log(err);
            res.status(400).send(err);
        }
        //console.log(result)
        res.status(200).send("finish")
    })

})


// ################################ Compliance
// post add data complicance
app.post('/api/insert_compliance', (req, res) => {

    //console.log(req.body)
    const sql = `
    INSERT INTO public.compliance_sepsis
    (
    follow_id,datetime_follow,
    hn_patient, an_patient, room_id, datetime, 
    staff_id, 
    note,
    qSOFA,
    history,history_admit,history_ATB,history_map,history_Infection,
    lab, lactate, ATB, specimen, image, 
    treatment,ATBhr, bolus, vasopressors, follow, goalachieve, 
    discharge,ATB_guide,Abnormal, followup,disease,nutrition, 
    total_compliance
    )
    VALUES('${req.body.follow_id}', '${req.body.datetime_follow}', 
    '${req.body.hn_patient}','${req.body.an_patient}','${req.body.room_id}', CURRENT_TIMESTAMP, 
    '', 
    '${req.body.note}',
    ${req.body.qSOFA},
    ${req.body.history},${req.body.history_admit},${req.body.history_ATB},${req.body.history_map},${req.body.history_Infection},
    ${req.body.lab},${req.body.lactate},${req.body.ATB},${req.body.specimen},${req.body.image},
    ${req.body.treatment},${req.body.ATBhr},${req.body.bolus},${req.body.vasopressors},${req.body.follow},${req.body.goalachieve},
    ${req.body.discharge},${req.body.ATB_guide},${req.body.Abnormal},${req.body.followup},${req.body.disease},${req.body.nutrition},
    ${req.body.total_compliance}
    )
    `;

    //console.log(sql)

    sepsisdb3.query(sql, function (err, result) {
        if (err) {
            console.log(err);
            res.status(400).send(err);
        }
        //console.log(result)
        res.status(200).send("finish")
    })

})

// table month
app.post('/api/compliance_month', (req, res) => {
    // //console.log(json)
    try{

    if(typeof req.body.parameter == 'number'){
        const sql = `
        select *
        from public.compliance_sepsis
        where date_part('month',datetime) =  '${req.body.parameter}'`
        // const sql = "SELECT * FROM pg_catalog.pg_tables";
        sepsisdb3.query(sql, function (err, result) {
            if (err) {
                console.log(err);
                res.status(400).send(err);
            }
            res.status(200).send(result.rows);
        })
    }
    }catch(e){
        //console.log(e)
        res.status(400)
    }

  
});

app.post('/api/compliance_stat', (req, res) =>{
    try{
        if(typeof req.body.parameter == 'number'){
            const sql = `
            select 
            count(*) as total , 
            round(avg(total_compliance),1) as avg, 
            min(total_compliance), 
            max(total_compliance) 
            from public.compliance_sepsis
            where date_part('month',datetime) =  '${req.body.parameter}'`
            // const sql = "SELECT * FROM pg_catalog.pg_tables";
            sepsisdb3.query(sql, function (err, result) {
                if (err) {
                    console.log(err);
                    res.status(400).send(err);
                }
                // convert sting to object 
                // const obj = JSON.parse(result.rows[0]);
                // response status and data
                // //console.log(result.rows)
                res.status(200).send(result.rows);
            })
        }
    }catch(e){
        //console.log(e)
        res.status(400)
    }
    

});

// month report
app.post('/api/compliance_stat_month', (req, res) =>{
    try{
        if(typeof req.body.parameter == 'number'){
            const sql = `
            select 
            date_part('day',datetime) as day,
            round(avg(qSOFA),1) as qSOFA,
            round(avg(history),1) as History,
            round(avg(lab),1) as Lab, 
            round(avg(treatment),1) as Treatment_plan,
            round(avg(discharge),1) as Discharge_plan,
            round(avg(total_compliance),1) as Total
            from public.compliance_sepsis 
            where date_part('month',datetime) = ${req.body.parameter}
            group by date_part('day',datetime); `
            // const sql = "SELECT * FROM pg_catalog.pg_tables";
            sepsisdb3.query(sql, function (err, result) {
                if (err) {
                    console.log(err);
                    res.status(400).send(err);
                }
                // convert sting to object 
                // const obj = JSON.parse(result.rows[0]);
                // response status and data
                // //console.log(result.rows)
                res.status(200).send(result.rows);
            })
        }
    }catch(e){
        //console.log(e)
        res.status(400)
    }
    

});

// search by an
app.post('/api/compliance_search', (req, res) =>{
    try{
        if(typeof req.body.parameter == "string"){
            const sql = `
        select *
        from public.compliance_sepsis
        where an_patient = '${req.body.parameter}'`
            // const sql = "SELECT * FROM pg_catalog.pg_tables";
            sepsisdb3.query(sql, function (err, result) {
                if (err) {
                    console.log(err);
                    res.status(400).send(err);
                }
                // convert sting to object 
                // const obj = JSON.parse(result.rows[0]);
                // response status and data
                // //console.log(result.rows)
                res.status(200).send(result.rows);
            })
        }
    }catch(e){
        //console.log(e)
        res.status(400)
    }
    

});

// search stat by an
app.post('/api/compliance_stat_by_an', (req, res) =>{
    try{
        if(typeof req.body.parameter == "string"){
            const sql = `
            select
            round(avg(total_compliance),1) as avg
            from public.compliance_sepsis
            where an_patient = '${req.body.parameter}'`
            // const sql = "SELECT * FROM pg_catalog.pg_tables";
            sepsisdb3.query(sql, function (err, result) {
                if (err) {
                    console.log(err);
                    res.status(400).send(err);
                }
                // convert sting to object 
                // const obj = JSON.parse(result.rows[0]);
                // response status and data
                // //console.log(result.rows)
                res.status(200).send(result.rows);
            })
        }
    }catch(e){
        //console.log(e)
        res.status(400)
    }
    

});

// search lost by an
app.post('/api/compliance_lost_by_an', (req, res) =>{
    try{
        if(typeof req.body.parameter == "string"){
            const sql = `
            select
            count(*)
            from public.follow_sepsis
            where an_patient = '${req.body.parameter}' and status = 'active'`
            // const sql = "SELECT * FROM pg_catalog.pg_tables";
            sepsisdb3.query(sql, function (err, result) {
                if (err) {
                    console.log(err);
                    res.status(400).send(err);
                }
                // convert sting to object 
                // const obj = JSON.parse(result.rows[0]);
                // response status and data
                // //console.log(result.rows)
                res.status(200).send(result.rows);
            })
        }
    }catch(e){
        //console.log(e)
        res.status(400)
    }
    

});

// api/compliance_person
app.post('/api/compliance_person', (req, res) => {
    // //console.log(json)

    if(req.body.parameter === 'year'){
    var count = json.length
    var weight_score = 10
    var baseline = count * 10
    var qSOFA = 0 
    var history=0
    var history_admit = 0
    var history_ATB = 0
    var history_Infection = 0 
    var history_map = 0
    var lab = 0
    var lactate = 0
    var ATB = 0 
    var specimen= 0 
    var image= 0 
    var treatment= 0 
    var ATBhr= 0 
    var bolus= 0 
    var vasopressors= 0 
    var follow= 0 
    var goalachieve= 0 
    var discharge= 0 
    var ATB_guide= 0 
    var Abnormal= 0 
    var followup= 0 
    var disease= 0 
    var nutrition = 0
    var total_compliance = 0
    var total_compliance2 = 0

    for (var i = 0; i < json1.length; i++) {
        // value[i] = `('${result[i].HN}',to_char(current_timestamp, 'DD/MM/YY HH24:MI'),'${result[i].AN}',1) ` 
        // //console.log(json1[i].AN)
        history = history + parseInt(json1[i].history)
        history_admit = history_admit + parseInt(json1[i].history_admit)
        history_ATB = history_ATB + parseInt(json1[i].history_ATB)
        history_Infection = history_Infection + parseInt(json1[i].history_Infection)
        qSOFA = qSOFA + parseInt(json1[i].qSOFA)
        history_map = history_map + parseInt(json1[i].history_map)
        lab = lab + parseInt(json1[i].lab)
        lactate = lactate + parseInt(json1[i].lactate)
        ATB = ATB + parseInt(json1[i].ATB)
        specimen= specimen + parseInt(json1[i].specimen)
        image= image + parseInt(json1[i].image)
        treatment= treatment + parseInt(json1[i].treatment)
        //console.log(treatment)
        ATBhr= ATBhr + parseInt(json1[i].ATBhr)
        bolus= bolus + parseInt(json1[i].bolus)
        vasopressors= vasopressors + parseInt(json1[i].vasopressors)
        follow= follow + parseInt(json1[i].follow)
        goalachieve= goalachieve + parseInt(json1[i].goalachieve)
        discharge= discharge + parseInt(json1[i].discharge)
        ATB_guide= ATB_guide + parseInt(json1[i].ATB_guide)
        Abnormal= Abnormal + parseInt(json1[i].Abnormal)
        followup= followup + parseInt(json1[i].followup)
        disease= disease + parseInt(json1[i].disease)
        nutrition = nutrition + parseInt(json1[i].nutrition)
        total_compliance = total_compliance + parseInt(json1[i].total_compliance)
        total_compliance2 = total_compliance2 + parseInt(json1[i].total_compliance)

    }


    // //console.log("Patients : "+ count)
    // //console.log("history_admit % : " +(history_admit/count)*weight_score)
    // //console.log("history_ATB % : " +(history_ATB/count)*weight_score)
    // //console.log("history_Infection % : " +(history_Infection/count)*weight_score)
    // //console.log("history_map % : " +(history_map/count)*weight_score)
    // //console.log("qSOFA % : " +(qSOFA/count)*weight_score)
    // //console.log("Lab :" +(lab/count)*weight_score)
    // //console.log("Lactate :" +(lactate/count)*weight_score)

    var obj ={ year:{
        // patient:count,
        qSOFA : (qSOFA/count)*weight_score,
        history : (history/count)*weight_score,
        // history_admit : (history_admit/count)*weight_score,
        // history_ATB : (history_ATB/count)*weight_score,
        // history_Infection : (history_Infection/count)*weight_score,
        // history_map : (history_map/count)*weight_score,
        lab : (lab/count)*weight_score,
        // lactate :(lactate/count)*weight_score,
        // ATB : (ATB/count)*weight_score,
        // specimen: (specimen/count)*weight_score,
        // image: (image/count)*weight_score,
        treatment: (treatment/count)*weight_score,
        // ATBhr: (ATBhr/count)*weight_score,
        // bolus: (bolus/count)*weight_score,
        // vasopressors: (vasopressors/count)*weight_score,
        // follow: (follow/count)*weight_score,
        // goalachieve: (goalachieve/count)*weight_score,
        discharge: (discharge/count)*weight_score,
        // ATB_guide: (ATB_guide/count)*weight_score,
        // Abnormal: (Abnormal/count)*weight_score,
        // followup: (followup/count)*weight_score,
        // disease:(disease/count)*weight_score,
        // nutrition : (nutrition/count)*weight_score,
        total_compliance : (total_compliance/(count*10))*10,
        // test:total_compliance
        },
        total_compliance2 : total_compliance2,
        original : json1
    }

    res.send(obj);
    }
});



// ################################ get home
// app.use("/", jwt({
//     secret : jwtSecret,
//     algorithms: ['HS256'],
//     getToken: function fromCookie (req) {
//       var token = req.cookies.access_token || req.body.access_token || req.query.access_token || req.headers['x-access-token'] ;
//       if (token) {
//         return token;
//       } 
//       return null;
//     }
//   }).unless({
//       path:[
//         '/',
//         '/login'
//       ]}
//   ));

app.use(express.static(path.resolve(__dirname, './Client/', 'build')));
app.get('*', (req, res,next) => {
    res.sendFile(path.resolve(__dirname, './Client', 'build', 'index.html'));
})


app.listen(PORT, () => {
    //console.log(`Server is running on port : ${PORT}`)
})


module.exports = app