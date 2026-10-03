import React from 'react';
import clsx from 'clsx';
import { twMerge } from 'tailwind-merge';

export default function Section({
  children,
  className = '',
  id,
  as: Component = 'section',
  ...props
}) {
  return (
    <Component
      id={id}
      className={twMerge(clsx('py-12 sm:py-16 md:py-24 relative', className))}
      {...props}
    >
      {children}
    </Component>
  );
}
