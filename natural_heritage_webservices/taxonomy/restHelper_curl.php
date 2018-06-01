<?php
ini_set('display_errors', 1);
ini_set('display_startup_errors', 1);
error_reporting(E_ALL);

//A)
//class doing the HTTP POST connection via cURL.
//3rd and 4th parameters of the contructor  are optional (define them only if here is a proxy between your server and the REST services)

 /**
 * backbone of the code based on "A sample class to read HTTP headers"
 * @author Geoffray Warnants - http://www.geoffray.be 
 *(lines added by F Theeten for POST and Proxy connection)
 */

 class HTTPReaderCURLEDIT {
 protected $_url = null;
 protected $_headers = array();
 protected $_body = '';

 public function __construct( $url, $proxy_url='', $proxy_login='', $header='Content-Type: text/xml') 
 {
	
	 $this->_url = curl_init();
	 curl_setopt($this->_url, CURLOPT_FRESH_CONNECT, TRUE);
	 curl_setopt($this->_url, CURLOPT_RETURNTRANSFER, true);
	 if(strlen($proxy_url)>0)
	 {
	 	curl_setopt($this->_url, CURLOPT_PROXY, $proxy_url);
	 }
	 if(strlen($proxy_login)>0)
	 {	
	    curl_setopt($this->_url, CURLOPT_PROXYUSERPWD, $proxy_login);
	 }
	    curl_setopt($this->_url, CURLOPT_HEADER, 0);

	if($header!='raw')
	{
	
	     curl_setopt($this->_url, CURLOPT_HTTPHEADER, array($header));
	}
	    curl_setopt($this->_url, CURLOPT_URL, $url);
           curl_setopt($this->_url, CURLOPT_HEADERFUNCTION, array($this, 'readHeaders'));


 }
 
 
 public function __destruct() {
 curl_close($this->_url);
 }
 
 // this must be called from outside  to do the connection
 public function getHeaders() {

 $this->_body = curl_exec($this->_url);
 return $this->_headers;
 }
 
 public function getHeadersOnly()
{
	 return $this->_headers;
 }

 public function getBody() {
 return $this->_body;
 }
 
 protected function readHeaders($url, $str) {

 if (strlen($str) > 0) {
	 $this->_headers[] = $str;
 }

 return strlen($str);
 }
 }

//B
//function doing the connection and returning the result
function rest_helper($url, $header='Content-Type: text/xml')
{
	

	//mention your proxy parameters there in 3rd and 4th position (if needed)  
	$myObj=new HTTPReaderCURLEDIT($url,'','',$header);
	
	$headers=$myObj->getHeaders();
	
	$content = $myObj->getBody();
	$ret=Array();
	
	$ret[]=	$headers;
	$ret[]=	$content;
	return $ret;
	
		  	  
		  	  
}

?>
