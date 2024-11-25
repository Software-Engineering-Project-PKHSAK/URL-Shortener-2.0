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

const extractDataForVisualization = (linkEngagements: any, type: string, key: string) => {
  const counts: Record<string, number> = {};

  const visualization_data: [[string, string | number]] = [
    [type, "Count"]
  ]
  if(linkEngagements && linkEngagements.length > 0) {
    linkEngagements.forEach((engagement:any) => {
      if(engagement[key]) {
        counts[engagement[key]] = counts[engagement[key]]  || 0;
        counts[engagement[key]]++;
      }
    })
    for (const key in counts) {
      visualization_data.push([key, counts[key]]);
    }
  }
  return visualization_data;
}

const getbrowserVisualizationData = (linkEngagements: any) => extractDataForVisualization(linkEngagements, "Browser", "device_browser");
const getDeviceOSVisualizationData = (linkEngagements: any) => extractDataForVisualization(linkEngagements, "Device OS", "device_os");
const getDeviceTypeVisualizationData = (linkEngagements: any) => extractDataForVisualization(linkEngagements, "Device Type", "device_type");

export const ViewLinkDrawer = ({ openedLink, setOpenedLink }: any) => {
  const { id } = openedLink || {};
  const { data: linkEngagements, isLoading } = useFetchLinkEngagements(
    id,
    openedLink
  );

  const browser_visualization_data = getbrowserVisualizationData(linkEngagements);
  // Add stylings
  const browser_barOptions = {
    chartArea: { width: "70%" },
    hAxis: {},
    vAxis: {},
    legend: { position: "bottom" },
  };
  const deviceOS_visualization_data = getDeviceOSVisualizationData(linkEngagements);
  // Add stylings
  const os_barOptions = {
    chartArea: { width: "70%" },
    hAxis: {},
    vAxis: {},
    legend: { position: "bottom" },
  };

  const deviceType_visualization_data = getDeviceTypeVisualizationData(linkEngagements);
  const donutOptions = {
    pieHole: 0.4,
    is3D: false,
  }
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
      width={600}
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
          <div>
            <h4> A/B Sankey: </h4>
            <Chart
              chartType="Sankey"
              width="100%"
              height="300px"
              data={ab_visualization_data}
              options={sankeyOptions}
              />
          </div>
        }
      {deviceType_visualization_data.length > 1 && <div>
        <h4> Device Type: </h4>
        <Chart
          chartType="PieChart"
          width="100%"
          height="400px"
          data={deviceType_visualization_data}
          options={donutOptions}
        />
      </div>}
      {deviceOS_visualization_data.length > 1 && <div>
        <h4> OS Popularity: </h4>
        <Chart
        chartType="BarChart"
        width="100%"
        height="400px"
        data={deviceOS_visualization_data}
        options={os_barOptions}
      />
      </div>}
      {browser_visualization_data.length > 1 && <div>
        <h4 style={{marginTop: "20px"}}> Browser Popularity: </h4>
        <Chart
        chartType="BarChart"
        width="100%"
        height="400px"
        data={browser_visualization_data}
        options={browser_barOptions}
      />
      </div>}
    </Drawer>
  );
};
