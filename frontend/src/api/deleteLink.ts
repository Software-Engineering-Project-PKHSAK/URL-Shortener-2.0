import { useMutation } from "@tanstack/react-query";
import axios from "axios";

export const useDeleteLink = () => {
  const mutation = useMutation({
    mutationFn: async (id: any) => {
      const URLshortenerUser = window.localStorage.getItem("URLshortenerUser");
      let user_id = (URLshortenerUser && JSON.parse(URLshortenerUser).id) || {};
      const response = await axios.delete(
        `${process.env.REACT_APP_API_BASE_URL}/links/delete/${id}?user_id=${user_id}`,
        {
          headers: {
            "Content-Type": "application/json",
          },
        }
      );
      return response.data;
    },
  });

  return mutation;
};
