const data = $input.first().json.body || {};

const action = data.action || "updated";
const repository = data.repository || "unknown/repo";
const prNumber = data.pr_number || "?";
const title = data.title || "Untitled PR";
const url = data.url || "";
const author = data.author || data.sender || "unknown";
const base = data.base || "main";
const head = data.head || "unknown";
const isDraft = data.draft === true;
const merged = data.merged === true;
const labels = Array.isArray(data.labels)
  ? data.labels.map((l) => (typeof l === "string" ? l : l.name)).filter(Boolean)
  : [];
const reviewers = Array.isArray(data.requested_reviewers)
  ? data.requested_reviewers.map((r) => (typeof r === "string" ? r : r.login)).filter(Boolean)
  : [];

const statusMap = {
  opened: { color: 3447003, label: "🟢 PR opened" },
  reopened: { color: 10181046, label: "🟡 PR reopened" },
  ready_for_review: { color: 5763719, label: "👀 Ready for review" },
  synchronize: { color: 9807270, label: "🔄 New commits pushed" },
  closed: { color: merged ? 5763719 : 15158332, label: merged ? "🟣 PR merged" : "🔴 PR closed" },
};

const status = statusMap[action] || { color: 9807270, label: `ℹ️ ${action}` };

const fields = [
  { name: "Repository", value: repository, inline: true },
  { name: "Author", value: author, inline: true },
  { name: "PR", value: `#${prNumber}`, inline: true },
  { name: "Branches", value: `\`${head}\` → \`${base}\``, inline: false },
  { name: "Status", value: isDraft ? `${status.label} • Draft` : status.label, inline: true },
];

if (labels.length) {
  fields.push({ name: "Labels", value: labels.map((l) => `\`${l}\``).join(", "), inline: false });
}

if (reviewers.length) {
  fields.push({ name: "Requested reviewers", value: reviewers.map((r) => `@${r}`).join(", "), inline: false });
}

return [
  {
    json: {
      embeds: [
        {
          title: `PR #${prNumber} — ${title}`,
          url,
          description: `**${status.label}** in **${repository}**`,
          color: status.color,
          fields,
          footer: { text: "n8n demo • GitHub PR lifecycle" },
          timestamp: new Date().toISOString(),
        },
      ],
    },
  },
];
