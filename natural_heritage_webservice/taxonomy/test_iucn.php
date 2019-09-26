<?php
require_once("ParseIUCNJSON.php");
use \ForceUTF8\Encoding;

$elem = new ParseIUCNJSON("26558265ea2819cf63f860415f1e8d7829f427ddf7e505d19934278e77a6f72b","Tarentola mauritanica");

$tab=$elem->returnResult();

print_r($tab);

?>