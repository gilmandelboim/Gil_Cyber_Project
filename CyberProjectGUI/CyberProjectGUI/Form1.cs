using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Windows.Forms;
using System.Threading;
using System.IO.Pipes;
using System.IO;

namespace CyberProjectGUI
{
    public partial class Form1 : Form
    {
        public delegate void dele();
        /// <summary>
        /// Contains column names.
        /// </summary>
        string name="IP";

        /// <summary>
        /// Contains column data arrays.
        /// </summary>
        string[] dataArray=new string[0];

        public Form1()
        {
            InitializeComponent();

            
            // Render the DataGridView.
            dataGridView1.DataSource = GetResultsTable(this.name,this.dataArray);
            Thread engine = new Thread(new ThreadStart(PipeReader));
            engine.Start();

            NamedPipeServerStream server = new NamedPipeServerStream("Orders");
            //server.WaitForConnection();
            
        }

        public DataTable GetResultsTable(string name, string[] dataArray)
        {
            // Create the output table.
            DataTable d = new DataTable();
            d.Columns.Add(name);

             for(int i=0;i<dataArray.Length;i++)
                {
                    d.Rows.Add();
                }

                // Add each item to the cells in the column.
                for (int a = 0; a < dataArray.Length; a++)
                {
                    d.Rows[0][a] = dataArray[a];
                }

            // Loop through all process names.
          
            return d;
        }




        public void PipeReader()
        {
            // Open the named pipe.
            var server = new NamedPipeServerStream("NPtest1");

            //Console.WriteLine("Waiting for connection...");
            server.WaitForConnection();

            //Console.WriteLine("Connected.");
            var br = new BinaryReader(server);
            //var bw = new BinaryWriter(server);

            while (true)
            {
                try
                {
                    var len = (int)br.ReadUInt32();            // Read string length
                    if (len == 0)
                        continue;
                    var str = new string(br.ReadChars(len));    // Read string
                    string[] ips = str.Split(';');

                    this.dataArray = ips;
                    
                     
                    
                    

                    dele invokeDELE = new dele(this.updateDataGrid);
                    this.Invoke(invokeDELE);

                   


                    //Console.WriteLine("Read: " + str);
                }
                catch (EndOfStreamException)
                {
                    break;                    // When client disconnects
                }
            }

            MessageBox.Show("Engine has disconnected");
            server.Close();
            server.Dispose();

        }

        public void updateDataGrid() 
        {
            dataGridView1.DataSource = typeof(DataTable);
            dataGridView1.DataSource = GetResultsTable(this.name,this.dataArray);
        }

        private void dataGridView1_CellClick(object sender, DataGridViewCellEventArgs e)
        {
            //DataGridViewImageCell cell = (DataGridViewImageCell)dataGridView1.Rows[e.RowIndex].Cells[e.ColumnIndex];
           // if (cell.Value == null || cell.Value == "")
             //   return;
            DataGridView dataGridView2 = new DataGridView();
            dataGridView2.Parent = this;
            dataGridView2.Location = new Point(200, 499);

            //var server = new NamedPipeServerStream("NPtest2");

            ////Console.WriteLine("Waiting for connection...");
            //server.WaitForConnection();

            ////Console.WriteLine("Connected.");
            //var br = new BinaryReader(server);
            //string[] pr;
            //while (true)
            //{
            //    try
            //    {
            //        var len = (int)br.ReadUInt32();            // Read string length
            //        if (len != 0)
            //        {
                        
            //            var str = new string(br.ReadChars(len));    // Read string
            //            pr = str.Split(';');
            //            break;
            //        }


            //    }
            //    catch (EndOfStreamException)
            //    {
            //        // When client disconnects
            //    }

            //}
            string[] pr=new string[1];
            pr[0] = "asda";
            dataGridView2.DataSource = GetResultsTable("Procceses", pr);
            
        }











    }
}
