import React, { ButtonHTMLAttributes } from "react";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "default" | "outline" | "gradient" | "ghost";
  size?: "sm" | "md" | "lg";
}

export const Button: React.FC<ButtonProps> = ({
  children,
  className = "",
  variant = "default",
  size = "md",
  ...props
}) => {
  const baseStyles =
    "rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50 transition-all duration-300 transform hover:scale-105 active:scale-95 font-medium disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none";

  const sizeStyles = {
    sm: "px-3 py-2 text-sm",
    md: "px-4 py-2 text-base",
    lg: "px-6 py-3 text-lg",
  };

  const variantStyles = {
    default:
      "bg-blue-500 text-white hover:bg-blue-600 shadow-lg hover:shadow-xl",
    outline:
      "border-2 border-gray-300 bg-transparent text-gray-700 hover:bg-gray-100 hover:border-gray-400",
    gradient:
      "bg-gradient-to-r from-blue-500 to-purple-600 text-white hover:from-blue-600 hover:to-purple-700 shadow-lg hover:shadow-xl",
    ghost: "bg-transparent text-gray-600 hover:bg-gray-100 hover:text-gray-800",
  };

  return (
    <button
      className={`${baseStyles} ${sizeStyles[size]} ${variantStyles[variant]} ${className}`}
      {...props}
    >
      {children}
    </button>
  );
};
