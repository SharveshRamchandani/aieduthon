import React from "react";
import styled from "styled-components";

const slides = [
  "https://images.unsplash.com/photo-1522202176988-66273c2fd55f",
  "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee",
  "https://images.unsplash.com/photo-1498050108023-c5249f4df085",
];

const VerticalCarousel = () => {
  const quantity = slides.length;
  
  return (
    <StyledWrapper style={{ '--height': '100%', '--quantity': quantity } as React.CSSProperties}>
      <div className="slider">
        <div className="list">
          {slides.map((src, index) => (
            <div
              key={index}
              className="item"
              style={{ '--position': index + 1 } as React.CSSProperties}
            >
              {/* Bootstrap-like carousel-item */}
              <div className="carousel-item">
                <img src={src} alt={`Slide ${index + 1}`} />
              </div>
            </div>
          ))}
        </div>
      </div>
    </StyledWrapper>
  );
};

const StyledWrapper = styled.div`
  width: 100%;
  height: 100%;
  min-height: 300px;

  .slider {
    width: 100%;
    height: 100%;
    min-height: 300px;
    overflow: hidden;
    position: relative;

    /* 👇 control spacing here */
    --gap: 200px;
  }

  .list {
    position: relative;
    width: 100%;
    height: 100%;
    min-height: 300px;
  }

  .item {
    width: 100%;
    height: 100%;
    min-height: 300px;
    position: absolute;
    top: 100%;

    animation: verticalRun 30s linear infinite;
    animation-delay: calc(
      (30s / var(--quantity)) * (var(--position) - 1) - 30s
    );
  }

  /* ✅ spacing is handled here */
  @keyframes verticalRun {
    from {
      top: calc(100% + var(--gap));
    }
    to {
      top: calc(-100% - var(--gap));
    }
  }

  .carousel-item {
    width: 100%;
    height: 100%;
    box-sizing: border-box;
  }

  .carousel-item img {
    width: 100%;
    height: 100%;
    min-height: 200px;
    object-fit: cover;
    border-radius: 20px;
    display: block;
  }
`;



export default VerticalCarousel;
