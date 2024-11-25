import {
  Button,
  Collapse,
  DatePicker,
  Drawer,
  Input,
  Space,
  Switch,
  List,
  Typography,
  Form,
  Alert
} from "antd";
import { useCreateLink } from "api/createLink";
import { useVerifyStub } from "api/verifyStub";
import { stringify } from "querystring";
import { useState } from "react";
import Swal from "sweetalert2";
import { useEffect } from 'react'
import axios from "axios";

const { Panel } = Collapse;
const { Title } = Typography;

export const CreateLinkDrawer = ({
  openedCreateLink,
  setOpenedCreateLink,
}: any) => {
  const [isLoading, setIsLoading] = useState(false);
  const [isABValid, setIsABValid] = useState(true);
  const [payload, setPayload] = useState<any>({
    created_on: null,
    disabled: false,
    expire_on: null,
    long_url: null,
    stub: null,
    title: null,
    updated_on: null,
    utm_campaign: null,
    utm_content: null,
    utm_medium: null,
    utm_source: null,
    utm_term: null,
    max_visits: null,
    tags: [],
    ab_variants: []
  });
  const createLinkMutation = useCreateLink();

  const [customStubString, setCustomStubString] = useState<string>("");
  const [customStubValidation, setCustomStubValidation] = useState<string>("");
  const { isError: vs_isError, error: vs_error, data: vs_data, refetch: vs_refetch } = useVerifyStub(customStubString);
  
  useEffect(() => {
    if(!vs_isError && vs_data){
      const _payload = { ...payload };
      _payload["stub"] = customStubString === "" ? null : customStubString;
      setPayload(_payload);
    }
  }, [vs_data])
  console.log("Payload", payload)
  const handleCallVerify = (buttonEvent: any) => {
    const _payload = { ...payload };
    if(!/^[A-Za-z0-9\-_.~]*$/.test(customStubString)){
      setCustomStubValidation("Only A-Za-z0-9\-_.~ are allowed!")
    } else {
      console.log("Refetch requested");
      vs_refetch();
    }
  };

  const handleChange = (propertyName: string, e: any) => {
    const _payload = { ...payload };
    _payload[propertyName] = e.target.value;
    setPayload(_payload);
  };

  const handleDateChange = (value: any, dateString: any) => {
    const _payload = { ...payload };
    _payload["expire_on"] = value;
    setPayload(_payload);
  };

  const handleSwitchChange = (checked: boolean) => {
    const _payload = { ...payload };
    _payload["disabled"] = !checked;
    setPayload(_payload);
  };
  const handleTagsChange = (tags: string[]) => {
    const _payload = { ...payload, tags };
    setPayload(_payload);
  };

  const handleSubmit = async () => {
    setIsLoading(true);
    console.log("Hello rbuh", JSON.parse(JSON.stringify(payload)));
    createLinkMutation.mutate(payload, {
      onSuccess: () => {
        Swal.fire({
          icon: "success",
          title: "Link Created Successfully!",
          text: "You have successfully created a short link",
          confirmButtonColor: "#221daf",
        }).then(() => {
          window.location.reload();
        });
      },
      onError: () => {
        Swal.fire({
          icon: "error",
          title: "Link Creation Failed!",
          text: "An error occurred, please try again",
          confirmButtonColor: "#221daf",
        });
      },
    });
  };

  const onABURLChange = (index: number, url: string) => {
    const _payload = { ...payload };
    _payload.ab_variants[index] = _payload.ab_variants[index] || {};
    _payload.ab_variants[index]["url"] = url;
    if(url === "" || _payload.ab_variants[index]["percentage"] == null) {
      setIsABValid(false);
    } else {
      setIsABValid(true); 
    }
    setPayload(_payload);
  }

  const onABPercentageChange = (index: number, percentage: string) => {
    const _payload = { ...payload };
    _payload.ab_variants[index] = _payload.ab_variants[index] || {};
    _payload.ab_variants[index]["percentage"] = percentage;
    if(_payload.ab_variants[index]["url"] === "" || percentage == null) {
      setIsABValid(false);
    } else {
      setIsABValid(true);
    }
    setPayload(_payload);
  }

  const validateAllABVariants = () => {
    const _payload = { ...payload };
    const isValid = _payload.ab_variants.every((variant:any) => {
      return variant.url && variant.percentage != null;
    });
    setIsABValid(isValid);
  }

  const getSumOfABVariantsPercentages = () => {
    const _payload = { ...payload };
    let sum = 0;
    _payload.ab_variants.forEach((variant:any) => {
      sum += variant.percentage ? parseInt(variant.percentage): 0; 
    });
    return sum;
  }

  return (
    <Drawer
      title="Create Short URL"
      placement="right"
      onClose={() => setOpenedCreateLink(false)}
      open={openedCreateLink}
    >
      <div>
        <form>
          <div className="form-group">
            <label>Title *</label>
            <Input onChange={(e) => handleChange("title", e)} size="large" />
          </div>
          <div className="form-group">
            <label>Long URL *</label>
            <Input onChange={(e) => handleChange("long_url", e)} size="large" />
          </div>
          <div className="form-group">
            <label>Custom Short URL</label>
            <div className="form-group" style={{ display: "flex", alignItems: "center" }}>
              <Input
                onChange={(e) => {
                  const _payload = { ...payload };
                  _payload["stub"] = null;
                  setPayload(_payload);
                  setCustomStubValidation("");
                  setCustomStubString(e.target.value)
                }}
                size="large"
                style={{ marginRight: "10px" }} // Space between input and button
              />
              <Button
                size="large"
                onClick={handleCallVerify}
                disabled={!customStubString.trim()} // Button is disabled if input is empty
              >
                Verify
              </Button>
            </div>
            {vs_isError && (
              <Alert
                message="Error"
                description={axios.isAxiosError(vs_error) && vs_error.response?.data?.message || vs_error.message}
                type="error"
                showIcon
                style={{ marginTop: "0px" }} // Space between input/button and error message
              />
            )}
            {customStubValidation && (
              <Alert
                message="Error"
                description={customStubValidation}
                type="error"
                showIcon
                style={{ marginTop: "0px" }} // Space between input/button and error message
              />
            )}
            {!vs_isError && vs_data && (
              <Alert
                message="Success"
                description={vs_data.message}
                type="success"
                showIcon
                style={{ marginTop: "0px" }} // Space between input/button and error message
              />
            )}
          </div>
          <div className="form-group">
            <label>Tags (comma-separated)</label>
            <Input
              placeholder="Enter tags separated by commas"
              onChange={(e) => handleTagsChange(e.target.value.split(","))}
              size="large"
            />
          </div>
          <div className="form-group">
            <label>Max Visits (optional)</label>
            <Input
              type="number"
              min="1"
              placeholder="Enter maximum number of visits"
              onChange={(e) => handleChange("max_visits", e)}
              size="large"
            />
          </div>
          <div className="form-group">
            <span style={{ marginRight: "10px" }}>Enabled?</span>
            <Switch defaultChecked onChange={handleSwitchChange} />
          </div>
          <div className="form-group">
            <Collapse onChange={() => null}>
              <Panel header="UTM Parameters For Tracking (optional)" key="1">
                <div className="form-group">
                  <label>UTM Source (optional)</label>
                  <Input
                    onChange={(e) => handleChange("utm_source", e)}
                    size="large"
                  />
                </div>
                <div className="form-group">
                  <label>UTM Medium (optional)</label>
                  <Input
                    onChange={(e) => handleChange("utm_medium", e)}
                    size="large"
                  />
                </div>
                <div className="form-group">
                  <label>UTM Campaign (optional)</label>
                  <Input
                    onChange={(e) => handleChange("utm_campaign", e)}
                    size="large"
                  />
                </div>
                <div className="form-group">
                  <label>UTM Term (optional)</label>
                  <Input
                    onChange={(e) => handleChange("utm_term", e)}
                    size="large"
                  />
                </div>
                <div className="form-group">
                  <label>UTM Content (optional)</label>
                  <Input
                    name="utm_content"
                    onChange={(e) => handleChange("utm_content", e)}
                    size="large"
                  />
                </div>
              </Panel>
              <Panel header="Short Link Availability" key="2">
                <div className="form-group">
                  <label>Password (optional)</label>
                  <Input
                    onChange={(e) => handleChange("password_hash", e)}
                    size="large"
                  />
                </div>
                <div className="form-group">
                  <label>Expire on (optional)</label>
                  <DatePicker showTime onChange={handleDateChange} />
                </div>
              </Panel>
              <Panel header="A/B Testing" key="3">
              <Form
                name="dynamic_form_nest_item"
                style={{
                  maxWidth: 600,
                }}
                autoComplete="off"
              >
                <Form.List name="users">
                  {(fields, { add, remove }) => (
                    <>
                      {fields.map(({ key, name, ...restField }, index) => (
                        <Space
                          key={key}
                          style={{
                            display: 'flex',
                            marginBottom: 8,
                          }}
                          align="baseline"
                        >
                          <Form.Item
                            {...restField}
                            name={[name, 'ab_url']}
                            rules={[
                              {
                                validator: (_, value) => {
                                  if (value === undefined || value === "") {
                                    setIsABValid(false);
                                    return Promise.reject(new Error("URL is required"));
                                  }
                                  if (value === payload.long_url) {
                                    setIsABValid(false);
                                    return Promise.reject(new Error("URL cannot be same as long URL"));
                                  }
                                  return Promise.resolve();
                                },
                              }
                            ]}
                          >
                          <Input 
                            placeholder="URL" 
                            onChange={(e) =>
                              onABURLChange(index, e.target.value)
                            }/>
                          </Form.Item>
                          <Form.Item
                            {...restField}
                            name={[name, "percentage"]}
                            rules={[
                              {
                                validator: (_, value) => {
                                  if (value === undefined || value === "") {
                                    setIsABValid(false);
                                    return Promise.reject(new Error("Percentage is required"));
                                  }
                                  if (value < 0 || value > 100) {
                                    setIsABValid(false);
                                    return Promise.reject(new Error("Percentage must be between 0 and 100"));
                                  }
                                  if(getSumOfABVariantsPercentages() > 100){
                                    setIsABValid(false);
                                    return Promise.reject(new Error("All percentages' sum must be less than 100"));
                                  }
                                  return Promise.resolve();
                                },
                              }
                            ]}
                          >
                          <Input 
                            placeholder="Percentage" 
                            type="number"
                            min={0} 
                            max={100}
                            onChange={(e) =>
                              onABPercentageChange(index, e.target.value)
                            }/>
                          </Form.Item>
                          <Button type="link" onClick={() => {remove(name); validateAllABVariants()}}> X </Button>
                        </Space>
                      ))}
                      <Form.Item>
                        <Button type="dashed" onClick={() => {add(); setIsABValid(false);}} block>
                          + Add Item
                        </Button>
                      </Form.Item>
                    </>
                  )}
                </Form.List>
              </Form>
              </Panel>
            </Collapse>
          </div>
          <div className="form-group">
            <Space>
              <Button
                size={"large"}
                onClick={() => setOpenedCreateLink(false)}
                disabled={isLoading || !isABValid}
              >
                Cancel
              </Button>
              <Button
                size={"large"}
                onClick={handleSubmit}
                type="primary"
                disabled={isLoading || !isABValid}
                loading={isLoading}
              >
                Submit
              </Button>
            </Space>
          </div>
        </form>
      </div>
    </Drawer>
  );
};
