import { useQuery } from "@tanstack/react-query";
import axios from "axios";

export const useFetchLinksByTags = (tags: any) => {
  const query = useQuery({
    queryKey: ["links"],
    queryFn: async () => {
      const JSON_WEB_TOKEN = window.localStorage.getItem("JSON_WEB_TOKEN");
      const tagsParam = tags.join(",");
      const response = await axios.get(
        `${process.env.REACT_APP_API_BASE_URL}/links?tags=${tagsParam}`,
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