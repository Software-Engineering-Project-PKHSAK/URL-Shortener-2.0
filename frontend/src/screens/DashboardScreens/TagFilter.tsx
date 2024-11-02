import { Dropdown, Space, Checkbox } from "antd";
import type { MenuProps } from "antd";
import { DownOutlined } from "@ant-design/icons";
import { useState } from "react";

export const TagFilter = ({
  tags,
  onTagSelect,
}: {
  tags: string[] | null;
  onTagSelect: (selectedTags: string[]) => void;
}) => {
  const [selectedTags, setSelectedTags] = useState<string[]>([]);

  const handleTagChange = (tag: string, checked: boolean) => {
    const updatedTags = checked
      ? [...selectedTags, tag]
      : selectedTags.filter((t) => t !== tag);
    setSelectedTags(updatedTags);
    onTagSelect(updatedTags); // Pass selected tags to parent
  };

  const tagItems = tags?.map((tag: string, index: number) => ({
    key: index + 1,
    label: (
      <Checkbox
        checked={selectedTags.includes(tag)}
        onChange={(e) => handleTagChange(tag, e.target.checked)}
      >
        <p style={{ fontWeight: "bold" }}>{tag}</p>
      </Checkbox>
    ),
  }));

  return (
    <div>
      <Dropdown menu={{ items: tagItems }}>
        <a onClick={(e) => e.preventDefault()} style={{ color: "black" }}>
          <Space>
            Tags
            <DownOutlined />
          </Space>
        </a>
      </Dropdown>
    </div>
  );
};
