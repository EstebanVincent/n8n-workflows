const data = $input.first().json.body || {};

const reviewState = data.review_state || data.action || "submitted";

const reviewMap = {
  approved: { color: 5763719, label: "✅ Review approved" },
  changes_requested: { color: 15158332, label: "❌ Changes requested" },
  commented: { color: 16098851, label: "💬 Review submitted" },
};

const review = reviewMap[reviewState] || { color: 9807270, label: `ℹ️ Review ${reviewState}` };

const fields = [
  { name: "PR", value: `#${data.pr_number || "?"}`, inline: true },
  { name: "Repository", value: data.repository || "unknown/repo", inline: true },
  { name: "Reviewer", value: data.author || data.sender || "unknown", inline: true },
  { name: "Title", value: data.title || "Untitled PR", inline: false },
  { name: "Review state", value: reviewState, inline: true },
];

if (data.comment_body) {
  fields.push({ name: "Review note", value: data.comment_body.slice(0, 1000), inline: false });
}

return [
  {
    json: {
      embeds: [
        {
          title: `${review.label} on PR #${data.pr_number}`,
          url: data.url || "",
          description: `Review event in **${data.repository || "unknown/repo"}**`,
          color: review.color,
          fields,
          footer: { text: "n8n demo • PR review" },
          timestamp: new Date().toISOString(),
        },
      ],
    },
  },
];
