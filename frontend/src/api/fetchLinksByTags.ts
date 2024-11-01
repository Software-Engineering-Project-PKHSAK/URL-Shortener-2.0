import { useQuery } from "@tanstack/react-query";
import axios from "axios";

export const useFetchLinksByTags = (tags: any) => {
  const query = useQuery({
    queryKey: ["links"],
    queryFn: async () => {
      const URLshortenerUser = window.localStorage.getItem("URLshortenerUser");
      let user_id = (URLshortenerUser && JSON.parse(URLshortenerUser).id) || {};
      const tagsParam = tags.join(",");
      const response = await axios.get(
        `${process.env.REACT_APP_API_BASE_URL}/links?user_id=${user_id}&tags=${tagsParam}`
      );
      return response.data;
    },
  });
  return query;
};