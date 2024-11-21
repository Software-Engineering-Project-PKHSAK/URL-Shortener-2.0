import { Drawer } from "antd";
import { useFetchLinkEngagements } from "api/fetchLinkEngagements";
import { stringify } from "querystring";
import { Chart } from "react-google-charts";

const getABVisualizationData = (openedLink: any, linkEngagements: any) => {
  const long_url_counts: Record<string, number> = {};
  const ab_visualization: [[string, string, string | number, any]] = [
    ["From", "To", "Count", { role: "tooltip", type: "string" }]
  ];
  if(openedLink && openedLink.ab_variants && openedLink.ab_variants.length > 0 && linkEngagements) {
    linkEngagements.forEach((engagement:any) => {
      if(engagement.long_url) {
        long_url_counts[engagement.long_url] = long_url_counts[engagement.long_url] || 0;
        long_url_counts[engagement.long_url]++;
      }
    })
    for (const key in long_url_counts) {
      ab_visualization.push([("Hits:"+linkEngagements.length.toString()), key, long_url_counts[key], key + ":" + (long_url_counts[key].toString())]);
    }
  }
  return ab_visualization;
}
export const ViewLinkDrawer = ({ openedLink, setOpenedLink }: any) => {
  const { id } = openedLink || {};
  const { data: linkEngagements, isLoading } = useFetchLinkEngagements(
    id,
    openedLink
  );

  const ab_visualization_data = getABVisualizationData(openedLink, linkEngagements);
  const sankeyOptions = {
    sankey: {
      node: {
        label: 
          { fontName: 'Times-Roman',
            fontSize: 14,
            color: '#000000D9',
            bold: true,
            italic: false
          },
      },
    },
  };
  return (
    <Drawer
      title="URL Engagement Analytics"
      placement="right"
      onClose={() => setOpenedLink(null)}
      open={openedLink}
    >
      <div>
        {isLoading ? (
          "fetching link details"
        ) : (
          <div>
            <h3>Total number of visits: {linkEngagements?.length}</h3>
          </div>
        )}
      </div>
      {ab_visualization_data.length > 1 && 
        <><h4> A/B Sankey: </h4>
        <Chart
          chartType="Sankey"
          width="100%"
          height="300px"
          data={ab_visualization_data}
          options={sankeyOptions}
        /></>
      }
    </Drawer>
  );
};
