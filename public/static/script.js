function upload_file(event){
  event.preventDefault();
  var name = document.getElementById("name").value;
  var fileInput = document.getElementById('fileToUpload');
  var file = fileInput.files[0];

  var formData = new FormData();
  formData.append('name', name);
  formData.append('file', file);
  var xhr = new XMLHttpRequest();
  load();
  xhr.open('POST', '/upload', true);
  // xhr.setRequestHeader('Content-Type', 'application/octet-stream');
  xhr.onreadystatechange = function() {
  
    if (xhr.readyState == XMLHttpRequest.DONE) {
      if (xhr.status == 200) {
        console.log('success')
        console.log(xhr.responseText)
        viewSDF();
        viewSVG(name);
        hide_mol_table();

      }
      else {
        console.log('Error')
      }
    }
  };
  xhr.send(formData)
  console.log(name)
  console.log(file)
}

function view_mol_table(){
  document.getElementById('molTable').style.display = 'block';

}

function hide_mol_table(){
  document.getElementById('molTable').style.display = 'none';
}

function viewSDF() {
  var x = document.getElementById("view");
  var y = document.getElementById("upload");
  var z = document.getElementById("element");
  x.style.display = "block";
  y.style.display = "none";
  z.style.display = "none";

  console.log("viewSDF");
  $.ajax({
    url: "/view",
    type: "GET",
    dataType: "json",
    success: function (response) {
      console.log("success");
      var html_str = "";
      console.log(response.length);
      for (let i = 0; i < response.length; i++) {
        html_str +=
          "<tr class='sdf_row'><td>" +
          response[i].id +
          "</td><td>" +
          response[i].name +
          "</td>";
        html_str +=
          "<td><button type='button' onclick='viewSVG(" +
          '"' +
          response[i].name +
          '"' +
          ")'> View SVG</button></td></tr>";
      }
      console.log("before append");
      console.log(html_str);
      $(".sdf_row").remove();
      $("#molTable").append(html_str);
    },
    error: function (response) {
      console.log("error");
      console.log(response);
    },
  });
  view_mol_table();
}

function load(){
  document.getElementById('uploadForm').style.display = 'none';
  document.getElementById('loading').style.display = 'block';
}

function viewSVG(name) {
  console.log(name);
  $.ajax({
    url: "/viewSVG",
    type: "POST",
    data: name,
    dataType: "xml",
    success: function (response) {
      console.log("viewSVG success");
      console.log(response);

      $(".viewMolecule").remove();
      $("#molView").html(response.documentElement.outerHTML);
    },
    error: function (response) {
      console.log("viewSVG error");
      console.log(response);
    },
  });
}

function viewUpload() {
  var x = document.getElementById("upload");
  var y = document.getElementById("view");
  var z = document.getElementById("element");
  document.getElementById('loading').style.display = 'none';
  document.getElementById('uploadForm').style.display = "block";
  x.style.display = "block";
  y.style.display = "none";
  z.style.display = "none";
}

function viewElement() {
    console.log("viewElement")
  var z = document.getElementById("element");
  var x = document.getElementById("upload");
  var y = document.getElementById("view");
  z.style.display = "block";
  x.style.display = "none";
  y.style.display = "none";
  $.ajax({
    url: "/viewElement",
    type: "GET",
    dataType: "json",
    success: function (response) {
      console.log(response);
      var html_str = "";
      for (let i = 0; i < response.length; i++) {
        console.log(response[i].elno);
        console.log(response[i].elcode);
        console.log(response[i].elname);
        console.log(response[i].col1);
        console.log(response[i].col2);
        console.log(response[i].col3);
        console.log(response[i].rad);
        html_str +=
          "<tr class='element_row'><td>" +
          response[i].elno +
          "</td><td>" +
          response[i].elcode +
          "</td><td>" +
          response[i].elname +
          "</td><td>" +
          response[i].col1 +
          "</td><td>" +
          response[i].col2 +
          "</td><td>" +
          response[i].col3 +
          "</td><td>" +
          response[i].rad +
          "</td><td>" +
          "<button onclick='removeElement("
          + '"' + response[i].elcode + '"' + 
          ")'>Remove</button>" +
          "</td></tr>"
          ;
      }
      $(".element_row").remove();
      $("#elementTable").append(html_str);
    },
    error: function (response) {
      console.log(response);
    },
  });
}

function removeElement(elcode){
    console.log("removeElement");
    console.log(elcode);
    $.ajax({
        url: "/remove_element",
        type: "POST",
        data: elcode,
        success: function (response) {
            console.log("success")
            console.log(response);
            viewElement();
        },
        error: function (response) {
            console.log("error");
            console.log(response);
        }
    });
}

function rotateSVG(event){
  event.preventDefault();

  var direction = document.getElementById('selectRotation').value;
  var rotation = document.getElementById("rot").value;
  
  console.log(rotation);
  console.log(rotation);

  var xhr = new XMLHttpRequest();
  xhr.open("POST", "/rotation_values", true);
  xhr.setRequestHeader("Content-Type", "application/xml");
  xhr.onreadystatechange = function () {
    if (xhr.readyState == XMLHttpRequest.DONE) {
      if (xhr.status == 200) {
        console.log("success");
        var data = xhr.responseText;
        // console.log( data);
        $(".viewMolecule").remove();
        $("#molView").append(data);
      } else {
        console.log("error");
      }
    }
  };

  xhr.send(
    JSON.stringify({
      direction: direction,
      rotation: rotation,
    })
  );
};

function add_element(event){
  event.preventDefault();
  var elno = document.getElementById("elno").value;
  var elcode = document.getElementById("elcode").value;
  var elname = document.getElementById("elname").value;
  var col1 = document.getElementById("col1").value;
  var col2 = document.getElementById("col2").value;
  var col3 = document.getElementById("col3").value;
  var rad = document.getElementById("rad").value;
  
  var xhr = new XMLHttpRequest();
  xhr.open("POST", '/add_element', true);
  xhr.setRequestHeader('Content-Type', 'application/json');
  xhr.onreadystatechange = function() {
    if (xhr.readyState == XMLHttpRequest.DONE) {
      if (xhr.status == 200) {
        console.log('success')
        viewElement();
      }
      else {
        console.log('Error')
      }
    }
  };

  xhr.send(
    JSON.stringify({
      elno: elno,
      elcode: elcode,
      elname: elname,
      col1: col1,
      col2: col2,
      col3: col3,
      rad: rad,
    })
  );
};
