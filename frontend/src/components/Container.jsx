import React from 'react';
import clsx from 'clsx';
import { twMerge } from 'tailwind-merge';

export default function Container({
  children,
  className = '',
  size = 'default', // 'hero', 'default', 'compact'
  as: Component = 'div',
  ...props
}) {
  const sizeClasses = {
    hero: 'max-w-[1400px] w-full mx-auto px-4 sm:px-6 lg:px-8',
    default: 'max-w-[1200px] w-full mx-auto px-4 sm:px-6 lg:px-8',
    compact: 'max-w-[960px] w-full mx-auto px-4 sm:px-6 lg:px-8',
    full: 'w-full px-4 sm:px-6 lg:px-8',
  };

  return (
    <Component
      className={twMerge(clsx(sizeClasses[size] || sizeClasses.default, className))}
      {...props}
    >
      {children}
    </Component>
  );
}
