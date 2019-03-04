$my_bucket = us.artifacts.academic-veld-231919.appspot.com
$request_body = file_get_contents('php://input');
$data = json_decode($request_body);
$fp = fopen("gs://${my_bucket}/mostRecent.txt", "w");
fwrite($fp, $data);
fclose($fp);