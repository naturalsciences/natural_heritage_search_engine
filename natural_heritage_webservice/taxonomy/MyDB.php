<?php
class MyDB
{
    protected static $instance;
    protected $pdo;
    
     protected $user_name="natural_heritage_service";
     protected $password= 'naturalheritage_service_201$';
     
     public function __construct()
     {
        $this->pdo=new PDO("pgsql:dbname=naturalheritage_service;host=hystrix.rbins.be", $this->user_name, $this->password );
     }
     
   // a classical static method to make it universally available
    public static function instance()
    {
        if (self::$instance === null)
        {
            self::$instance = new self;
        }
        return self::$instance;
    }
    
    public  function getPDO()
    {
        if (self::$instance === null)
        {
            self::$instance = new self;
        }
        $var=self::$instance;
        return $var->pdo;
        
    }
    
    // a proxy to native PDO methods
    /*public function __call($method, $args)
    {
        return call_user_func_array(array($this->pdo, $method), $args);
    }*/
        
}

?>