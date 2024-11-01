import { useEffect, useState } from "react";
import { Drawer } from "antd";
import http from "utils/api";

const ViewLinkDrawer = ({ openedLink, setOpenedLink }: any) => {
  const URLshortenerUser = window.localStorage.getItem("URLshortenerUser");
  let user_id = (URLshortenerUser && JSON.parse(URLshortenerUser).id) || {};

  const { id, long_url } = openedLink || {};
  const [isLoading, setIsLoading] = useState(false);
  const [payload, setPayload] = useState<any>(openedLink);
  const [engagements, setEngagements] = useState<any[]>([]);

  useEffect(() => {
    if (openedLink) {
      fetchLink();
      fetchLinkEngagements();
      setPayload(openedLink);
    }
  }, [openedLink]);

  const fetchLink = async () => {
    setIsLoading(true);
    await http
      .get(`http://localhost:5002/links/${id}`, payload)
      .then((res) => {
        setIsLoading(false);
      })
      .catch((err) => {
        setIsLoading(false);
      });
  };

  const fetchLinkEngagements = async () => {
    setIsLoading(true);
    await http
      .get(
        `http://localhost:5002/links/${id}/engagements?user_id=${user_id}`,
        payload
      )
      .then((res) => {
        const _engagements = res.data?.engagements;
        setIsLoading(false);
        setEngagements(_engagements);
      })
      .catch((err) => {
        setIsLoading(false);
      });
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
            <h3>No of visits: {engagements?.length}</h3>
          </div>
        )}
      </div>
    </Drawer>
  );
};
