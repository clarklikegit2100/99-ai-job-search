import type { TemplatePageProps } from "../../document";
import { StyleSheet, Text } from "#react-pdf-renderer";
import { useRender } from "../../context";

const styles = StyleSheet.create({
	footer: {
		position: "absolute",
		left: 0,
		right: 0,
		fontFamily: "Helvetica",
		fontSize: 7.5,
		textAlign: "center",
		opacity: 0.65,
	},
});

/** A fixed footer rendered by React PDF on every exported resume page. */
type PageNumberFooterProps = Pick<TemplatePageProps, "pageSize">;

export const PageNumberFooter = ({ pageSize }: PageNumberFooterProps) => {
	const { metadata } = useRender();
	const isFreeForm = typeof pageSize === "object";
	// Bottom offsets are resolved against the full wrapped flow by React PDF.
	// A fixed top coordinate anchors the footer to each physical A4/Letter page.
	const edgeStyle = isFreeForm ? { bottom: 8 } : { top: pageSize === "LETTER" ? 774 : 824 };

	return (
		<Text
			fixed={!isFreeForm}
			style={[styles.footer, edgeStyle, { color: metadata.design.colors.text }]}
			render={({ pageNumber, totalPages }) => `Page ${pageNumber} of ${totalPages}`}
		/>
	);
};
