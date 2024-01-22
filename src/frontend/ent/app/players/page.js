"use client"
import { useEffect, useState } from "react";
import {
  CircularProgress,
  Pagination,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
} from "@mui/material";
import { useRouter } from "next/router";
import axios from "axios";

export default function DisastersPage() {
  const router = useRouter();
  const searchParams = useSearchParams(); // Adicione esta linha
  const pathname = usePathname(); // Adicione esta linha

  const createQueryString = (name, value) => {
    const params = new URLSearchParams(searchParams);
    params.set(name, value);

    return params.toString();
  };

  const [data, setData] = useState(null);
  const [maxDataSize, setMaxDataSize] = useState(0);
  const page = parseInt(searchParams.get("page")) || 1;
  const PAGE_SIZE = 10;

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get("http://api-entities:8080/disasters");
        setData(response.data.data);
        setMaxDataSize(response.data.total);
      } catch (error) {
        console.error("Error fetching data:", error);
      }
    };

    fetchData();
  }, [page]);

  return (
    <>
      <h1 sx={{ fontSize: "100px" }}>Disasters</h1>

      <TableContainer component={Paper}>
        <Table sx={{ minWidth: 650 }} aria-label="simple table">
          <TableHead>
            <TableRow sx={{ backgroundColor: "lightgray" }}>
              <TableCell component="th" width={"1px"} align="center">
                ID
              </TableCell>
              <TableCell>Date</TableCell>
              <TableCell>Aircraft Type</TableCell>
              <TableCell>Operator</TableCell>
              <TableCell>Fatalities</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {data ? (
              data.map((row) => (
                <TableRow key={row.id}>
                  <TableCell component="td" align="center">
                    {row.id}
                  </TableCell>
                  <TableCell component="td" scope="row">
                    {row.Date}
                  </TableCell>
                  <TableCell component="td" scope="row">
                    {row.AircraftType}
                  </TableCell>
                  <TableCell component="td" scope="row">
                    {row.Operator}
                  </TableCell>
                  <TableCell component="td" scope="row">
                    {row.Fatalities}
                  </TableCell>
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell colSpan={5}>
                  <CircularProgress />
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>
      {maxDataSize && (
        <Pagination
          style={{ color: "black", marginTop: 8 }}
          variant="outlined"
          shape="rounded"
          color={"primary"}
          onChange={(e, v) => {
            router.push(router.pathname + "?" + createQueryString("page", v));
          }}
          page={page}
          count={Math.ceil(maxDataSize / PAGE_SIZE)}
        />
      )}
    </>
  );
}
