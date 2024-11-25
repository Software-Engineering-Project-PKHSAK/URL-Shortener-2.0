import { useQuery } from "@tanstack/react-query";
import axios from "axios";

export const useFetchStats = () => {
  const query = useQuery({
    queryKey: ["stats"],
    queryFn: async () => {
      const JSON_WEB_TOKEN = window.localStorage.getItem("JSON_WEB_TOKEN");
      const response = await axios.get(
        `${process.env.REACT_APP_API_BASE_URL}/links/stats`,
        {
          headers: {
             Authorization: `Bearer ${JSON_WEB_TOKEN}`,
          },
        }
      );
      return response.data;
    },
  });
  return query;
};
