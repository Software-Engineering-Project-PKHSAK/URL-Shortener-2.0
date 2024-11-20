import { useEffect, useState } from "react";
import { useLocation, useParams } from "react-router";
import ShortUrlRedirectionPage from "screens/ErrorScreens/ShortUrlRedirectionPage";
import Swal from "sweetalert2";
import http from "../../utils/api";
import "./styles.scss";

const RedirectionPage = () => {
  const { pathname } = useLocation();
  const params = useParams() || {};
  const stub = params?.stub || params["*"];

  let dateTime = new Date();
  const [endpoint1Called, setEndpoint1Called] = useState(false);

  const [errorPage, setErrorPage] = useState<boolean>(false);

  useEffect(() => {
    if (!endpoint1Called) {
      fetchURL();
    }
  }, []);

  const fetchURL = async () => {
    const url = pathname.startsWith("/a/")
      ? `http://localhost:8080/${stub}`
      : `http://localhost:8080/${stub}`;
    await http
      .get(url)
      .then(async (res) => {
        setEndpoint1Called(true);
        const { link } = res.data || {};
        const {
          id: link_id,
          disabled,
          expire_on,
          long_url,
          password_hash,
          utm_source,
          utm_medium,
          utm_campaign,
          utm_term,
          utm_content,
        } = link || {};
        const isExpired =
          (expire_on && new Date(expire_on) > dateTime) || false;
        if (disabled == false && !password_hash && !isExpired) {
          return window.location.assign(long_url);
        } else if (disabled == true || isExpired) {
          Swal.fire({
            icon: "error",
            title: "Oops, this link is no longer active!",
            text: "It has either expired or has been disabled by the owner",
            confirmButtonColor: "#221daf",
          });
        } else if (password_hash) {
          Swal.fire({
            title: "Enter password for authetication",
            input: "text",
            inputAttributes: {
              autocapitalize: "off",
            },
            showCancelButton: true,
            confirmButtonText: "Submit",
            showLoaderOnConfirm: true,
            preConfirm: (password) => {
              if (password == link.password_hash) {
                window.location.assign(link.long_url);
              } else {
                Swal.showValidationMessage(
                  `Incorect password. Request failed!`
                );
              }
            },
          });
        }
      })
      .catch((err) => {
        setErrorPage(true);
        // errorPage = <ShortUrlRedirectionPage />
      });
  };

  if (errorPage) {
    return <ShortUrlRedirectionPage />;
  }
  return <div></div>;
};

export default RedirectionPage;
