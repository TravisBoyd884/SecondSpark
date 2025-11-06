import { GlobeAltIcon } from "@heroicons/react/24/outline";
import Image from "next/image";

export default function SecondSparkLogo() {
  return (
    <Image
      src="/Second.png"
      width={500}
      height={500}
      className="md:w-48 md:h-48 w-15 h-15"
      alt="SecondSpark Logo"
    />
  );
}
