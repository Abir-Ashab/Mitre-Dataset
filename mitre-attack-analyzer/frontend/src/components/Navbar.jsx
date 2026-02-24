import { NavLink } from "react-router-dom";
import { LayoutDashboard, FileText, FolderOpen } from "lucide-react";

const navigation = [
  {
    name: "Dataset Overview",
    path: "/",
    icon: LayoutDashboard,
    exact: true,
  },
  {
    name: "Single Analysis",
    path: "/analyze",
    icon: FileText,
  },
  {
    name: "Session Manager",
    path: "/sessions",
    icon: FolderOpen,
  },
];

export default function Navbar() {
  return (
    <nav className="bg-white dark:bg-gray-800 rounded-lg p-1 inline-flex shadow-sm border border-gray-200 dark:border-gray-700">
      {navigation.map((item) => (
        <NavLink
          key={item.path}
          to={item.path}
          end={item.exact}
          className={({ isActive }) =>
            `px-4 py-2 rounded-md text-sm font-medium transition-colors flex items-center gap-2 ${
              isActive
                ? "bg-primary-600 text-white"
                : "text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
            }`
          }
        >
          <item.icon className="w-4 h-4" />
          {item.name}
        </NavLink>
      ))}
    </nav>
  );
}
