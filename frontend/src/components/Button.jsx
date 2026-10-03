import React from 'react';
import { motion } from 'motion/react';
import clsx from 'clsx';
import { twMerge } from 'tailwind-merge';

export default function Button({
  children,
  variant = 'primary',
  size = 'md',
  className = '',
  disabled = false,
  onClick,
  type = 'button',
  icon: Icon,
  iconPosition = 'left',
  ...props
}) {
  const baseStyles = 'inline-flex items-center justify-center font-medium transition-all duration-200 select-none cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed focus-visible:outline-2 focus-visible:outline-offset-2';

  const sizeStyles = {
    sm: 'text-xs px-3.5 py-1.5 rounded-full gap-1.5',
    md: 'text-sm px-5 py-2.5 rounded-full gap-2',
    lg: 'text-base px-6 py-3 rounded-full gap-2.5 font-semibold',
  };

  const variantStyles = {
    primary: 'bg-[#0a152d] text-white hover:bg-[#152445] active:bg-[#070e20] shadow-sm focus-visible:outline-[#0a152d]',
    secondary: 'bg-white text-[#0a1b33] border border-gray-200 hover:bg-gray-50 hover:border-gray-300 shadow-xs focus-visible:outline-gray-400',
    outline: 'bg-transparent text-[#0a1b33] border border-gray-300 hover:bg-gray-100/60 focus-visible:outline-gray-400',
    ghost: 'bg-transparent text-[#0a1b33] hover:bg-gray-100/80 focus-visible:outline-gray-400',
    subtle: 'bg-gray-100 text-[#0a1b33] hover:bg-gray-200 focus-visible:outline-gray-400',
  };

  const merged = twMerge(
    clsx(
      baseStyles,
      sizeStyles[size] || sizeStyles.md,
      variantStyles[variant] || variantStyles.primary,
      className
    )
  );

  return (
    <motion.button
      type={type}
      whileHover={disabled ? {} : { scale: 1.015 }}
      whileTap={disabled ? {} : { scale: 0.985 }}
      className={merged}
      disabled={disabled}
      onClick={onClick}
      {...props}
    >
      {Icon && iconPosition === 'left' && <Icon className={size === 'sm' ? 'w-3.5 h-3.5' : size === 'lg' ? 'w-5 h-5' : 'w-4 h-4'} />}
      <span>{children}</span>
      {Icon && iconPosition === 'right' && <Icon className={size === 'sm' ? 'w-3.5 h-3.5' : size === 'lg' ? 'w-5 h-5' : 'w-4 h-4'} />}
    </motion.button>
  );
}
