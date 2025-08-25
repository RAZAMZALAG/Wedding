import React, { useState } from "react";
import { CardMedia } from "@mui/material";
import placeHolderImage from "../assets/tool_placeholder.svg";

const ItemImage = ({ item, width = "100%" }) => {
  const [imageSrc, setImageSrc] = useState(
    `${import.meta.env.VITE_API_URL}/catalog/${item.name}.png`,
  );

  const handleImageError = () => {
    setImageSrc(placeHolderImage);
  };

  return (
    <CardMedia
      component="img"
      image={imageSrc}
      alt={item.name}
      onError={handleImageError}
      sx={{
        width: width,
        height: 200,
        objectFit: "fill", // <-- will stretch to fill the box
        backgroundColor: "#f5f5f5",
        display: "block",
        mx: "auto",
      }}
    />
  );
};

export default ItemImage;
