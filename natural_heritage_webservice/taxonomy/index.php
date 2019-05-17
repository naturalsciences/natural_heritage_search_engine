<html>
<head>
 <meta charset="UTF-8">
<meta http-equiv="cache-control" content="max-age=0" />
<meta http-equiv="cache-control" content="no-cache" />
<meta http-equiv="expires" content="0" />
<meta http-equiv="expires" content="Tue, 01 Jan 1980 1:00:00 GMT" />
<meta http-equiv="pragma" content="no-cache" />
 <link rel="stylesheet" href="css/style.css"> 
</head>
<body>
<?php session_start();?>
<?php session_regenerate_id(FALSE);?>
<script src="../js/jquery-3.4.1.min.js"></script> 
<h1>Welcome to the Natural Heritage taxonomy checker</h1>
<form id="form_taxonomy" action="parse_file.php" method="post" enctype="multipart/form-data">
<table>
<tr>
<td>   
	<br>Mail :
    
</td>
<td>

<input type="mail" name="mail" id="mail"></input>
<br/>
<div id="mail_message" style="color:red"></div>
</td>
</tr>
<tr>
<td>
    Select Tab-delimited to upload:
</td>
<td>
    <input type="file" name="file_to_upload" id="file_to_upload">
</td>
</tr>
<tr>
<td>   
    <br>Has header row :
</td>
<td>
    <input id="headers" name="headers" type="checkbox" checked>
</td>
</tr>
<tr>
<td>   
    <br>Column index of the name field (first = 1) :
</td>
<td>
    <input type="text" name="pos_data_field" id="pos_data_field"></input>
</td>
</tr>
<tr>
<td>   
	<br>Column index of the kingdom field (first = 1) [optional] :
</td>
<td>
<input type="text" name="pos_kingdom_field" id="pos_kingdom_field"></input>
</td>
</tr>
</tr>
	
</table>
<table>
	  <tr><td>DARWIN (RBINS):</td><td> <input id="source_darwin" name="source_darwin" type="checkbox" ></td></tr>
      <tr><td>GBIF: </td><td><input id="source_gbif" name="source_gbif" type="checkbox"  checked></td></tr>
	  <tr><td>GBIF (Vernacular names):</td><td> <input id="source_gbif_vernacular" name="source_gbif_vernacular" type="checkbox" ></td></tr>
	  <tr><td>IUCN: </td><td><input id="source_iucn" name="source_iucn" type="checkbox" > </td></tr>
      <tr><td>WORMS: </td><td><input id="source_worms" name="source_worms" type="checkbox"> </td></tr>
</table>
	<input  name="submit" type="submit" value="send"/>
	</form>
 <script language="javascript">
         function isEmail(email) {
          var regex = /^([a-zA-Z0-9_.+-])+\@(([a-zA-Z0-9-])+\.)+([a-zA-Z0-9]{2,4})+$/;
          return regex.test(email);
        }
    var check_mail=function()
        {
            if(!isEmail($("#mail").val()))
            {
                console.log("invlaid");
                $("#mail_message").html("Invalid email");
                 $(':input[type="submit"]').prop('disabled', true);
            }
            else
            {
                $("#mail_message").html("");
                 $(':input[type="submit"]').prop('disabled', false);
            }
        }
      
    $("#mail").change(
        function()
        {
            check_mail();
       })  ;     
 </script>
</body>
</html>