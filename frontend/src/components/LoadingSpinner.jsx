export default function LoadingSpinner({ size = "md", text = "Loading...", className = "" }) {
  const sizeClasses = {
    sm: "h-4 w-4",
    md: "h-6 w-6", 
    lg: "h-8 w-8",
    xl: "h-12 w-12"
  };

  return (
    <div className={`flex items-center justify-center space-x-2 ${className}`}>
      <div className={`animate-spin rounded-full border-b-2 border-blue-600 ${sizeClasses[size]}`}></div>
      {text && <span className="text-gray-600 dark:text-gray-400">{text}</span>}
    </div>
  );
} 