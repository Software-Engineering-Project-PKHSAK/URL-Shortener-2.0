import { Popconfirm, Tag } from "antd";
import { useState } from "react";
import toast, { Toaster } from "react-hot-toast";
import QRCode from "react-qr-code";
import { QuestionCircleOutlined } from "@ant-design/icons";
import moment from "moment";
import { useDeleteLink } from "api/deleteLink";
import Swal from "sweetalert2";

export const LinkCardItem = ({
  setOpenedLink,
  setOpenedViewLink,
  item,
}: any) => {
  const {
    id,
    title,
    stub,
    long_url,
    created_on,
    disabled,
    max_visits = Infinity,
    visit_count = 0,
    tags,
  } = item || {};

  const [isDeleting, setIsDeleting] = useState(false);

  const URLshortenerUser = window.localStorage.getItem("URLshortenerUser");
  let user_id = (URLshortenerUser && JSON.parse(URLshortenerUser).id) || {};

  const deleteLinkMutation = useDeleteLink();

  const handleCopy = async () => {
    const text = `${process.env.REACT_APP_API_BASE_URL}/${stub}`;
    if ("clipboard" in navigator) {
      await navigator.clipboard.writeText(text);
    } else {
      document.execCommand("copy", true, text);
    }
    toast("URL copied successfully!", {
      icon: "👏",
      style: {
        borderRadius: "10px",
        background: "#333",
        color: "#fff",
      },
    });
  };

  const handleCopyQRCode = () => {
    const svgElement = document.getElementById(`qr-gen${id}`);
    
    if (svgElement) {
      // Serialize the SVG element to a string
      const serializer = new XMLSerializer();
      const svgString = serializer.serializeToString(svgElement);

      // Copy to clipboard
      navigator.clipboard.writeText(svgString).then(
        () => Swal.fire({
          icon: "success",
          title: "QR code copied!",
          text: "SVG code copied to clipboard!",
          confirmButtonColor: "#221daf",
        }),
        (err) => Swal.fire({
          icon: "error",
          title: "Couldn't copy QR code",
          text: "Unable to copy SVG code to clipboard!",
          confirmButtonColor: "#221daf",
        })
      );
    } else {
      alert("SVG element not found!");
    }
  };
  //   const downloadQRCode = () => {
  //     // Generate download with use canvas and stream
  //     const canvas = document.getElementById("qr-gen") as HTMLCanvasElement;;
  //     if (canvas) {
  //       const pngUrl = canvas
  //         .toDataURL("image/png")
  //         .replace("image/png", "image/octet-stream");
  //       let downloadLink = document.createElement("a");
  //       downloadLink.href = pngUrl;
  //       downloadLink.download = `qrcode.png`;
  //       document.body.appendChild(downloadLink);
  //       downloadLink.click();
  //       document.body.removeChild(downloadLink);
  //     }
  //   };

  //   const handleDisableEnableLink = async (e: any) => {
  //     e.preventDefault();
  //     const payload = {
  //       // ...item,
  //       long_url,
  //       disabled: !disabled,
  //     };

  //     await http
  //       .patch(
  //         `http://localhost:5002/links/update/${id}?user_id=${user_id}`,
  //         payload
  //       )
  //       .then((res) => {
  //         const { id } = res.data;
  //         Swal.fire({
  //           icon: "success",
  //           title: `Link ${disabled ? "Enabled" : "Disabled"} Successfully!`,
  //           text: "You have successfully updated this link",
  //           confirmButtonColor: "#221daf",
  //         }).then(() => {
  //           window.location.reload();
  //         });
  //       })
  //       .catch((err) => {
  //         Swal.fire({
  //           icon: "error",
  //           title: `Link ${disabled ? "Enabling" : "Disabling"} Failed!`,
  //           text: "An error occurred, please try again",
  //           confirmButtonColor: "#221daf",
  //         });
  //       });
  //   };

  const handleDeleteLink = async (e: any) => {
    e.preventDefault();

    setIsDeleting(true);
    deleteLinkMutation.mutate(id, {
      onSuccess: () => {
        Swal.fire({
          icon: "success",
          title: `Link Deleted Successfully!`,
          text: "You have successfully deleted this link",
          confirmButtonColor: "#221daf",
        }).then(() => {
          setIsDeleting(false);
          window.location.reload();
        });
      },
      onError: () => {
        Swal.fire({
          icon: "error",
          title: `Link Deletion Failed!`,
          text: "An error occurred, please try again",
          confirmButtonColor: "#221daf",
        });
        setIsDeleting(false);
      },
    });
  };
  const isExpired = visit_count >= max_visits;
  return (
    <div className="link-card">
      <div className="d-flex justify-content-between">
        <div className="col-lg-10">
          <h5>{title}</h5>
        </div>
        <div className="col-lg-2">
          <p className="time-text">
            <i className="fa-solid fa-clock"></i> {moment(created_on).fromNow()}
          </p>
        </div>
      </div>
      <div className="d-flex justify-content-between align-items-center">
        <div>
          <div className="url-pane">
            <a
              href={`${process.env.REACT_APP_API_BASE_URL}/${stub}`}
              rel="noreferrer"
              target="_blank"
            >
              <p>{`${process.env.REACT_APP_API_BASE_URL}/${stub}`}</p>
            </a>
            <i
              onClick={handleCopy}
              style={{ cursor: "pointer" }}
              className="fa-solid fa-copy"
            ></i>
          </div>
          <p style={{ overflowWrap: "break-word" }}>
            <b>Original URL:</b> {long_url}
          </p>
          <div className="btn-pane">
            {isExpired ? (
              <p style={{ color: "red" }}>
                <b>This link has expired due to reaching maximum visits.</b>
              </p>
            ) : (
              <>
                <button
                  className="btn btn-outline-dark"
                  onClick={() => setOpenedViewLink(item)}
                >
                  <i className="fa-solid fa-eye"></i> View Engagements Analytics
                </button>
                <button
                  className="btn btn-outline-primary"
                  onClick={() => setOpenedLink(item)}
                >
                  <i className="fa-solid fa-pen-to-square"></i> Edit
                </button>
                <button
                  className="btn btn-outline-primary"
                  onClick={() => handleCopyQRCode()}
                >
                  <i className="fa-solid fa-copy"></i> Copy QR
                </button>
              </>
            )}
            <Popconfirm
              title="Are you sure?"
              icon={<QuestionCircleOutlined style={{ color: "red" }} />}
              onConfirm={handleDeleteLink}
            >
              <button className="btn btn-outline-danger">
                <i className="fa-solid fa-trash"></i>{" "}
                {isDeleting ? "Deleting" : "Delete"}
              </button>
            </Popconfirm>
          </div>
        </div>
        <div>
          <QRCode id={"qr-gen"+id} value={long_url} size={100} level={"H"} />
        </div>
      </div>
      {tags.length > 0 && (
        <div style={{ marginTop: 8 }} className="d-flex">
          <p style={{ fontWeight: "bold", marginRight: 4 }}>Tags: </p>
          {tags.map((tag: any) => {
            return (
              <Tag className="link-tag" style={{ fontWeight: "bold" }}>
                {tag}
              </Tag>
            );
          })}
        </div>
      )}
      {/* <button className='btn btn-outline-dark'  onClick={downloadQRCode}>
            <i className="fa-solid fa-download"></i>
            Download QR Code
          </button> */}
    </div>
  );
};
