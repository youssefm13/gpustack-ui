export default function FileUploader({ onUpload }) {
  const handleChange = async (e) => {
    const file = e.target.files[0];
    const reader = new FileReader();

    reader.onload = () => {
      onUpload(reader.result);
    };

    reader.readAsText(file);
  };

  return <input type="file" onChange={handleChange} />;
}

