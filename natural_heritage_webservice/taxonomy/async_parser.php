<?php
namespace PHPMailer\PHPMailer;
require_once("csv_parser.php");
require('../vendor/autoload.php');


header('Content-Type: text/html; charset=utf-8');
header("Cache-Control: no-store, no-cache, must-revalidate, max-age=0");
header("Cache-Control: post-check=0, pre-check=0", false);
header("Pragma: no-cache");
?>
<?php

session_start();


$myParser= unserialize(base64_decode($_REQUEST["obj"]));

$myParser->parseFile();



//MAIL///////////////
/*$mail = new PHPMailer;



$mail->IsSMTP();                                      // Set mailer to use SMTP
$mail->Host = 'smtp.naturalsciences.be';                 // Specify main and backup server
$mail->Port = 25;                                    // Set the SMTP port
//$mail->SMTPAuth = true;                               // Enable SMTP authentication
//$mail->Username = '';                // SMTP username
//$mail->Password = '';                  // SMTP password
//$mail->SMTPSecure = 'tls';                            // Enable encryption, 'ssl' also accepted

$mail->From = 'darwin-ict@naturalsciences.be';
$mail->FromName = 'Naturalheritage';
$mail->AddAddress("franck.theeten@africamuseum.be");  // Add a recipient


$mail->IsHTML(true);                                  // Set email format to HTML

$mail->Subject = 'Taxon parsing finished';
$mail->Body    = 'Parsing finished, go to http://naturalheritage.africamuseum.be/natural_heritage_webservice/taxonomy/parse_file.php?id=".$_REQUEST["id"]';


if(!$mail->Send()) {
   echo 'Message could not be sent.';
   echo 'Mailer Error: ' . $mail->ErrorInfo;
   exit;
}

echo 'Message has been sent';
*/

?>