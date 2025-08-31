import React, { InputHTMLAttributes } from "react";

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  className?: string;
  variant?: "default" | "outline" | "filled" | "glass";
}

export const Input: React.FC<InputProps> = ({
  className = "",
  variant = "default",
  ...props
}) => {
  const baseStyles =
    "w-full px-4 py-3 rounded-lg focus:outline-none transition-all duration-300 font-medium";

  const variantStyles = {
    default:
      "theme-input focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50",
    outline:
      "border-2 theme-border bg-transparent focus:border-blue-500 focus:shadow-lg",
    filled:
      "theme-surface border-transparent focus:bg-white focus:shadow-lg focus:ring-2 focus:ring-blue-500",
    glass:
      "backdrop-blur-sm bg-white/10 border border-white/20 text-white placeholder-gray-300 focus:bg-white/20 focus:border-white/40 focus:shadow-xl",
  };

  return (
    <input
      className={`${baseStyles} ${variantStyles[variant]} ${className}`}
      {...props}
    />
  );
};
