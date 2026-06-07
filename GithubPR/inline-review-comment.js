const data = $input.first().json.body || {};

return [
  {
    json: {
      embeds: [
        {
          title: `🧵 Inline review comment on PR #${data.pr_number}`,
          url: data.comment_url || data.url || "",
          description: `**${data.sender || data.author || "Someone"}** left a code comment in **${data.repository || "unknown/repo"}**`,
          color: 15548997,
          fields: [
            { name: "Title", value: data.title || "Untitled PR", inline: false },
            { name: "Comment", value: (data.comment_body || "_No comment text_").slice(0, 1000), inline: false },
          ],
          footer: { text: "n8n demo • Inline review comment" },
          timestamp: new Date().toISOString(),
        },
      ],
    },
  },
];
