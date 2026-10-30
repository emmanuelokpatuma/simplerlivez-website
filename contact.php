<?php
// Simple contact handler for Hostinger shared hosting.
header('Content-Type: application/json');
if ($_SERVER['REQUEST_METHOD'] !== 'POST') { http_response_code(405); echo '{"ok":false}'; exit; }
if (!empty($_POST['website'])) { echo '{"ok":true}'; exit; } // honeypot: bots fill this
$clean = fn($k, $max = 200) => trim(mb_substr(str_replace(["\r", "\n"], ' ', strip_tags($_POST[$k] ?? '')), 0, $max));
$name = $clean('name'); $email = filter_var($_POST['email'] ?? '', FILTER_VALIDATE_EMAIL);
$company = $clean('company'); $interest = $clean('interest', 60);
$message = trim(mb_substr(strip_tags($_POST['message'] ?? ''), 0, 5000));
if (!$name || !$email || !$message) { http_response_code(400); echo '{"ok":false}'; exit; }
$to = 'hello@simplerlivez.com';
$subject = "Website enquiry: $interest – $name";
$body = "Name: $name\nEmail: $email\nCompany: $company\nInterest: $interest\n\n$message\n";
$headers = "From: SimplerLivez website <hello@simplerlivez.com>\r\nReply-To: $name <$email>\r\nContent-Type: text/plain; charset=UTF-8";
$ok = mail($to, $subject, $body, $headers, '-fhello@simplerlivez.com');
if (!$ok) http_response_code(500);
echo json_encode(['ok' => $ok]);
