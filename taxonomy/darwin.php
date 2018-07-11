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
DARWIN taxon checker
<form action="parse_darwin.php" method="post" enctype="multipart/form-data">
<table>
<tr>
<td>
    IP postgres:
</td>
<td>
    <input type="text" name="ip_postgres" id="ip_postgres" value="localhost">
</td>
</tr>
<tr>
<td>   
    Database name
</td>
<td>
     <input type="text" name="database" id="database" value="darwin2_rbins_migration">
</td>
</tr>
<tr>
<td>   
    User
</td>
<td>
    <input type="text" name="user" id="user" value="postgres">
</td>
</td>
</tr>
<tr>
<td>   
	Password
</td>
<td>
<input type="password" name="pwd" id="pwd">
</td>
</tr>
<tr>
<td>   
	Table name
</td>
<td>
<input type="text" name="table" id="table" value="darwin2.taxonomy">
</td>
</tr>
<tr>
<td>   
	Field name
</td>
<td>
<input type="text" name="field" id="field" value="name">
</td>
</tr>
<tr>
<td>   
	Output file path
</td>
<td>
<input type="text" name="output" id="output" value="/var/developments/output_darwin_worms" size="200">
</td>
</tr>	
</table>
      GBIF: <input id="source_gbif" name="source_gbif" type="checkbox"  checked>  <br/>
      WORMS: <input id="source_worms" name="source_worms" type="checkbox">  <br/>
	<input type="submit" value="send"/>
	</form>
</form>
</body>