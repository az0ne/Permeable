<?php
/*
����NB���ѵ�һ�Ŀ⣬�������ܴ���Ǹ���
*/
//�ݴ���ʱ����
ini_set('display_errors', 1);
set_time_limit(0);
error_reporting(E_ALL);
//�޸����������
$host="127.0.0.1"; //��������ַ
$user="root";      //�������û�
$password="root";  //����������
$db="tuolu";        //���ݿ�
$table="tuo";        //���ݿ��еı�
//��������
$conn = mysql_connect($host, $user, $password) or die("not connect:");
mysql_select_db($db,$conn) or die("Could not connect");
$result = mysql_query("SELECT * FROM $table",$conn) or die("not connect");
$num = 0;
$content = '';
echo "[+]�����ѿ���..."."<br>";
while ($row = mysql_fetch_row($result)) {
    $num = $num+1;
    $content .=  implode("|", $row)."\n";
	 if(!($num%5)){//5Ϊд���ļ�������
        $filename = 'c:/'.intval($num/5).'.xls';
        file_put_contents($filename,$content);
        $content = '';
    }
}
echo "[+]�ѿ����...";
mysql_free_result($result);
?>