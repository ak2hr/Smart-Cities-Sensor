$my_bucket = us.artifacts.academic-veld-231919.appspot.com
$fileContents = file_get_contents("gs://${my_bucket}/mostRecent.txt");
echo($fileContents);