import { useQuery } from "@tanstack/react-query";
import axios from "axios";

export const useFetchLinkEngagements = (id: any, openedLink: any) => {
  const query = useQuery({
    queryKey: ["link"],
    queryFn: async () => {
      const JSON_WEB_TOKEN = window.localStorage.getItem("JSON_WEB_TOKEN");
      const response = await axios.get(
        `${process.env.REACT_APP_API_BASE_URL}/links/${id}/engagements`,
        {
          headers: {
             Authorization: `Bearer ${JSON_WEB_TOKEN}`,
          },
        }
      );
      return response.data?.engagements;
    },
    enabled: !!openedLink,
  });
  return query;
};
