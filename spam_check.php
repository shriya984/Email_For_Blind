<?php
function is_spam($subject, $message, $threshold = 5.0) {
    $keywords = json_decode(file_get_contents("spam_keywords.json"), true);
    $text = strtolower($subject . " " . $message);
    $words = preg_split('/\s+/', preg_replace('/[^a-z0-9\s]/', ' ', $text));

    $score = 0;
    foreach($words as $w){
        if(isset($keywords[$w])){
            $score += $keywords[$w];
        }
    }

    return ["spam_score" => $score, "is_spam" => ($score >= $threshold ? 1 : 0)];
}
?>
