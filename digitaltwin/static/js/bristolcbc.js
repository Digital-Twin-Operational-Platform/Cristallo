var mode_fws = 1;
var mode_asw = 1;
var mode_cbc = 1;   // 1 forward, 2 backward, 0 idle

$(document).ready(function(){
  $("#fsw").click(function(){
      mode_fws = 1 // forward sweep
      setInterval(function() {
          if (mode_fws < 400) {
              ajaxfws();
              mode_fws++;

              //setTimeout(function() {status = ajaxchkmode();}, 2000);
              //status = ajaxchkmode();

              //if (status[0] == 0.0) {
            //      mode = 0;
              //};
          };

      }, 500);

      //$("h2").hide();
  });

  $("#asw").click(function(){
      mode_asw = 1 // forward sweep
      setInterval(function() {
          if (mode_asw < 81) {
              ajaxasw();
              mode_asw++;

              //setTimeout(function() {status = ajaxchkmode();}, 2000);
              //status = ajaxchkmode();

              //if (status[0] == 0.0) {
            //      mode = 0;
              //};
          };

      }, 500);
  });

  $("#cbc").click(function(){
      mode_cbc = 1 // forward sweep
      setInterval(function() {
          if (mode_cbc < 101) {
              ajaxcbc();
              mode_cbc++;

              //setTimeout(function() {status = ajaxchkmode();}, 2000);
              //status = ajaxchkmode();

              //if (status[0] == 0.0) {
            //      mode = 0;
              //};
          };

      }, 500);
  });
});

function ajaxfws() {

    $.ajaxSetup({async: false});


    $.ajax({
        url: "/bristolcbc_update_fws",
        type: "GET",
        contentType: 'application/json;charset=UTF-8',
        data: { value: mode_fws },
        dataType: "json",
        success: function (data) {
            Plotly.react("timehist", data);
        }
    });

}

function ajaxasw() {

    $.ajaxSetup({async: false});


    $.ajax({
        url: "/bristolcbc_update_asw",
        type: "GET",
        contentType: 'application/json;charset=UTF-8',
        data: { value: mode_asw },
        dataType: "json",
        success: function (data) {
            Plotly.react("timehist", data);
        }
    });

}

function ajaxcbc() {

    $.ajaxSetup({async: false});


    $.ajax({
        url: "/bristolcbc_update_cbc",
        type: "GET",
        contentType: 'application/json;charset=UTF-8',
        data: { value: mode_cbc },
        dataType: "json",
        success: function (data) {
            Plotly.react("timehist", data);
        }
    });

}

function ajaxchkmode() {
    $.ajaxSetup({async: false});

    $.ajax({
        url: "/bristolcbc_modecheck",
        type: "GET",
        contentType: 'application/json;charset=UTF-8',
        data: { value: mode },
        dataType: "json",
        success: function (data) {
            return(data);
        }
    });

}

function ajaxbws() {
    $.ajax({
        url: "/update_bws",
        type: "GET",
        contentType: 'application/json;charset=UTF-8',
        data: { value: count },
        dataType: "json",
        success: function (data) {
            Plotly.react('bargraph', data, layout = layout);
            console.log(count);
            if (count > 178) {
                count = 0;
            } else {
                count++;
            }
        }
    });
}
