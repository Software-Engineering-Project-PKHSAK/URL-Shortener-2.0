import { useMutation } from "@tanstack/react-query";
import axios from "axios";

export const useUpdateLink = () => {
  const mutation = useMutation({
    mutationFn: async ({ id, payload }: { id: any; payload: any }) => {
      const JSON_WEB_TOKEN = window.localStorage.getItem("JSON_WEB_TOKEN");
      const response = await axios.patch(
        `${process.env.REACT_APP_API_BASE_URL}/links/update/${id}`,
        payload,
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
