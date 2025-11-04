import React from 'react';

type GlassProps = {
  children?: React.ReactNode;
  className?: string;
  style?: React.CSSProperties;
};

export function GlassPanel({ children, className = '', style = {} }: GlassProps) {
  return (
    <div className={`glass-panel ${className}`} style={style}>
      {children}
    </div>
  );
}

export function GlassButton(props: React.ButtonHTMLAttributes<HTMLButtonElement> & { variant?: string }) {
  const { className = '', variant = 'primary', ...rest } = props;
  const base = `glass-button btn btn-${variant}`;
  return <button className={`${base} ${className}`} {...(rest as any)} />;
}

export default GlassPanel;
