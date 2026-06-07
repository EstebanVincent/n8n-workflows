const data = $input.first().json.body || {};

return [
  {
    json: {
      embeds: [
        {
          title: `💬 New PR comment on #${data.pr_number}`,
          url: data.comment_url || data.url || "",
          description: `**${data.sender || data.author || "Someone"}** commented on **${data.repository || "unknown/repo"}**`,
          color: 16098851,
          fields: [
            { name: "Title", value: data.title || "Untitled PR", inline: false },
            { name: "Comment", value: (data.comment_body || "_No comment text_").slice(0, 1000), inline: false },
          ],
          footer: { text: "n8n demo • PR conversation comment" },
          timestamp: new Date().toISOString(),
        },
      ],
    },
  },
];
