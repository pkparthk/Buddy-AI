import React, { ReactNode } from "react";

interface ScrollAreaProps {
  className?: string;
  children: ReactNode;
}

export const ScrollArea: React.FC<ScrollAreaProps> = ({
  className = "",
  children,
}) => {
  return <div className={`overflow-auto ${className}`}>{children}</div>;
};
