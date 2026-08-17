import { readdirSync, readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";

const sourceRoot = process.env.RR_SOURCE_ROOT ?? "/app";
const templatesRoot = join(sourceRoot, "packages/pdf/src/templates");
const importLine = 'import { PageNumberFooter } from "../shared/page-number-footer";';
const pageClose = "\n\t\t</Page>";
const footerAndClose = "\n\t\t\t<PageNumberFooter pageSize={pageSize} />\n\t\t</Page>";

let patched = 0;
for (const entry of readdirSync(templatesRoot, { withFileTypes: true })) {
	if (!entry.isDirectory() || entry.name === "shared") continue;

	const filename = join(templatesRoot, entry.name, `${entry.name[0].toUpperCase()}${entry.name.slice(1)}Page.tsx`);
	let source;
	try {
		source = readFileSync(filename, "utf8");
	} catch {
		continue;
	}

	if (source.includes(importLine) || source.includes("<PageNumberFooter")) {
		throw new Error(`Page-number patch was already applied: ${filename}`);
	}
	if (!source.includes(pageClose)) {
		throw new Error(`Could not locate the PDF Page closing tag: ${filename}`);
	}

	source = `${importLine}\n${source}`;
	source = source.replace(pageClose, footerAndClose);
	writeFileSync(filename, source, "utf8");
	patched += 1;
}

if (patched !== 15) {
	throw new Error(`Expected to patch 15 templates, but patched ${patched}. Upstream source may have changed.`);
}

console.log(`Injected automatic page numbers into ${patched} Reactive Resume templates.`);
