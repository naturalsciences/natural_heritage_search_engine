<?php
	class GetDataDB
	{
		
		public function getData($p_id)
		{
			 try
            {
				$flag_db=TRUE;
				
				if($flag_db)
				{
					print("finished");
					$db_driver=MyDB::instance();
					$sql= "SELECT * FROM  public.taxon_checker WHERE session = ? ORDER BY date_data; ";
					//$db_driver->getPdo()->beginTransaction();
					$stmt = $db_driver->getPdo()->prepare($sql);
					$session_tmp= $p_id;
					$stmt->execute([$p_id]);
					//$db_driver->getPdo()->commit();
					$fullResult=array();
					$i=0;
					$header=Array();
					foreach ($stmt as $row)
					{
						$result['src_data']=Array();
						$result['parsed_data']=Array();
						$tmpArray=json_decode($row["data"]);
						
						foreach($tmpArray as $col=>$val)
						{
							if($i==0)
							{
								$header[]=$col;
							}
							if(is_numeric($col))
							{
								$result['src_data'][$col]=$val;
							}
							else
							{
								$result['parsed_data'][$col]=$val;
							}
						}
						$fullResult[]=$result;
						$i++;
					}
					//print_r($fullResult);
				}
				$_SESSION[$p_id]["results"]=$fullResult;
				$_SESSION[$p_id]["headers"]=$header;
				$_SESSION[$p_id]["match_statistics"]=$this->getMatchingStatistics($p_id);
				
             }
             catch(PDOExeption $e)
            {
                print($e->getMessage());
            }
		}
		
		public function getMatchingStatistics($p_id)
		{
			$returned=Array();
			if(is_array($_SESSION[$p_id]["results"]))
			{
				foreach($_SESSION[$p_id]["results"] as $row)
				{
					if(array_key_exists('gbif_match_type',$row['parsed_data']))
					{
						$match=$row['parsed_data']['gbif_match_type'];
						//$match= preg_replace('/\(.+\)/','',$match);
						$synonym=$row['parsed_data']['gbif_name_status'];
						if(strpos($synonym, "synonym")!==FALSE and strpos($match, "synonym") ===FALSE)
						{
							$match.=" (+ synonymy)";
						}
						if(array_key_exists($match,$returned))
						{
							$returned[$match]["count"]=$returned[$match]["count"]+1;						
						}
						else
						{
							$returned[$match]["count"]=1;
							$returned[$match]["rgb_match_type"]=$row['parsed_data']['rgb_match_type'];
							$returned[$match]["background_style"]=$row['parsed_data']['background_style'];
						}
					}
				}
				
			}
			asort($returned);
			
			return $returned;
			
		}

		public function countData($p_id)
		{
			 try
            {
				$flag_db=TRUE;
				
				if($flag_db)
				{					
					$db_driver=MyDB::instance();
					$sql= "SELECT COUNT(*) as cpt FROM  public.taxon_checker WHERE session = ? ; ";
					//$db_driver->getPdo()->beginTransaction();
					$stmt = $db_driver->getPdo()->prepare($sql);
					$session_tmp= $p_id;
					$stmt->execute([$p_id]);
					//$db_driver->getPdo()->commit();
					$fullResult=array();
					$i=0;
					$header=Array();
					$cpt=0;
					foreach ($stmt as $row)
					{
						$cpt = $row['cpt'];
					}
					return $cpt;
					//print_r($fullResult);
				}
				
				
             }
             catch(PDOExeption $e)
            {
                print($e->getMessage());
            }
		}		
		
	}
?>