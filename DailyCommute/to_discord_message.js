const fs = require("fs");

function toDiscordMessage(data, commuteTime) {
    const rawData = (data && data.output) || {};

    const severityMap = {
        critical: { color: 15158332 },
        warning: { color: 15105570 },
        log: { color: 3066993 },
    };

    const overallSeverity = rawData.overall_severity || "log";
    const statusInfo = severityMap[overallSeverity] || severityMap.log;

    const finalTitle = `${commuteTime} Commute Status`;
    const finalColor = statusInfo.color;
    const finalDescription = `**${rawData.overall_summary || "No summary available"}**`;

    const finalFields = [];
    const lineReports = rawData.line_reports || [];

    for (const report of lineReports) {
        const lineName = report.line || "Unknown Line";
        const severity = report.severity;
        const summary = report.summary || "";

        let value = "❌ Disruption";
        if (severity === "log") {
            value = "✅ Normal service";
        } else if (severity === "warning") {
            value = `⚠️ Delays\n${summary}`;
        } else if (summary) {
            value = `❌ Disruption\n${summary}`;
        }

        finalFields.push({ name: lineName, value, inline: false });
    }

    const finalJson = {
        embed: {
            title: finalTitle,
            description: finalDescription,
            color: finalColor,
            author: "Commute Assistant",
            fields: finalFields,
            footer: { text: "Legend: ✅ Normal • ⚠️ Delays • ❌ Disruption" },
        },
    };

    return [{ json: finalJson }];
}

if (require.main === module) {
    const args = process.argv.slice(2);
    const getArgValue = (flag, fallback) => {
        const index = args.indexOf(flag);
        return index === -1 ? fallback : args[index + 1];
    };

    const jsonPath = getArgValue("--json-path", "DailyCommute/inputs/to_discord_message.json");
    const commuteTime = getArgValue("--commute-time", "Morning");

    try {
        const raw = fs.readFileSync(jsonPath, "utf-8");
        const data = JSON.parse(raw);
        const result = toDiscordMessage(data, commuteTime);
        console.log(JSON.stringify(result, null, 2));
    } catch (error) {
        console.error(`Error: ${error.message}`);
        process.exitCode = 1;
    }
} else {
    const data = $input.first().json;
    const commuteTime = ($node["Set commute"].json || {}).time || "Morning";
    return toDiscordMessage(data, commuteTime);
}
