import { useMutation } from "@tanstack/react-query";
import axios from "axios";

export const useCreateBulkLinks = () => {
  const mutation = useMutation({
    mutationFn: async ({ jsonPayload }: { jsonPayload: any }) => {
      const JSON_WEB_TOKEN = window.localStorage.getItem("JSON_WEB_TOKEN");
      const response = await axios.post(
        `${process.env.REACT_APP_API_BASE_URL}/links/create_bulk`,
        jsonPayload,
        {
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${JSON_WEB_TOKEN}`,
          },
        }
      );
      return response.data;
    },
  });

  return mutation;
};
