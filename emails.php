<?php
// --- DATABASE CONNECTION ---
$host = "localhost";
$user = "root";
$pass = "";
$db   = "imails";

$conn = new mysqli($host, $user, $pass, $db);
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

// --- LOAD SPAM KEYWORDS ---
$spam_keywords = json_decode(file_get_contents('spam_keywords.json'), true);
if (!$spam_keywords) {
    die("Could not load spam keywords JSON file.");
}

// --- FETCH EMAILS ---
$sql = "SELECT * FROM emails";
$result = $conn->query($sql);

// --- PROCESS EMAILS ---
while ($row = $result->fetch_assoc()) {
    $email_id = $row['id']; // change if your PK column name differs
    $subject  = $row['subject'];
    $body     = $row['body'];

    // Calculate spam score
    $spam_score = 0;
    foreach ($spam_keywords as $word) {
        if (stripos($subject . ' ' . $body, $word) !== false) {
            $spam_score++;
        }
    }

    // Determine if spam
    $is_spam = ($spam_score >= 2) ? 1 : 0;

    // Update DB with spam info
    $update = $conn->prepare("UPDATE emails SET is_spam = ?, spam_score = ? WHERE id = ?");
    $update->bind_param("iii", $is_spam, $spam_score, $email_id);
    $update->execute();
}

// --- DISPLAY EMAILS ---
echo "<h2>📬 Email Overview</h2>";

$count_inbox = $conn->query("SELECT COUNT(*) AS total FROM emails WHERE is_spam = 0")->fetch_assoc()['total'];
$count_spam  = $conn->query("SELECT COUNT(*) AS total FROM emails WHERE is_spam = 1")->fetch_assoc()['total'];
$count_sent  = $conn->query("SELECT COUNT(*) AS total FROM emails WHERE sender IS NOT NULL")->fetch_assoc()['total'];

echo "<p><strong>Inbox:</strong> $count_inbox</p>";
echo "<p><strong>Sent:</strong> $count_sent</p>";
echo "<p><strong>Spam:</strong> $count_spam</p>";
echo "<hr>";

$sql2 = "SELECT * FROM emails ORDER BY id DESC";
$result2 = $conn->query($sql2);

while ($row = $result2->fetch_assoc()) {
    echo "<div style='border:1px solid #ccc; padding:10px; margin:10px;'>";
    echo "<strong>From:</strong> " . htmlspecialchars($row['sender']) . "<br>";
    echo "<strong>To:</strong> " . htmlspecialchars($row['receiver']) . "<br>";
    echo "<strong>Subject:</strong> " . htmlspecialchars($row['subject']) . "<br>";
    echo "<strong>Body:</strong> " . htmlspecialchars($row['body']) . "<br>";
    echo "<strong>Spam Score:</strong> " . $row['spam_score'] . "<br>";

    if ($row['is_spam'] == 1) {
        echo "<span style='color:red; font-weight:bold;'>🛑 This is a spam email</span>";
    } else {
        echo "<span style='color:green; font-weight:bold;'>✅ Not spam</span>";
    }

    echo "</div>";
}

$conn->close();
?>
