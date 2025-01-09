import { ReactNode, forwardRef } from "react";

interface ScrollAreaProps {
  className?: string;
  children: ReactNode;
}

const ScrollArea = forwardRef<HTMLDivElement, ScrollAreaProps>(
  ({ className = "", children }: ScrollAreaProps, ref) => {
    return (
      <div className={`overflow-auto ${className}`} ref={ref}>
        {children}
      </div>
    );
  }
);

ScrollArea.displayName = "ScrollArea"; // Helps with debugging in React DevTools

export { ScrollArea };
