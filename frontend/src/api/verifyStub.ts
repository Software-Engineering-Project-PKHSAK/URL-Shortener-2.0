import { useQuery } from "@tanstack/react-query";
import axios from "axios";

export const useVerifyStub = (customStubString: String) => {
  const query = useQuery({
    queryKey: ["verifyStub",customStubString],
    queryFn: async () => {
      const URLshortenerUser = window.localStorage.getItem("URLshortenerUser");
      let user_id = (URLshortenerUser && JSON.parse(URLshortenerUser).id) || {};
      const response = await axios.get(
        `${process.env.REACT_APP_API_BASE_URL}/verify/${customStubString}?user_id=${user_id}`
      );
      return response.data;
    },
    enabled: false,
    refetchOnWindowFocus: false,
    retryOnMount: false,
    refetchOnMount: false,
    retry: 1,
  });
  return query;
};